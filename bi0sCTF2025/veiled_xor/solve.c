#include <assert.h>
#include <gmp.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define SIZE 1024
#define MAX_CANDIDATES 1000000

typedef struct {
  mpz_t p;
  mpz_t q;
} candidate_t;

typedef struct {
  candidate_t *candidates;
  int count;
  int capacity;
} candidate_list_t;

typedef struct {
  int thread_id;
  int start_idx;
  int end_idx;
  candidate_list_t *input_candidates;
  candidate_list_t *output_candidates;
  mpz_t n;
  mpz_t veil_xor;
  int mask_size;
  pthread_mutex_t *output_mutex;
} thread_data_t;

void init_candidate_list(candidate_list_t *list) {
  list->capacity = 10000;
  list->count = 0;
  list->candidates = malloc(list->capacity * sizeof(candidate_t));
  for (int i = 0; i < list->capacity; i++) {
    mpz_init(list->candidates[i].p);
    mpz_init(list->candidates[i].q);
  }
}

void add_candidate(candidate_list_t *list, mpz_t p, mpz_t q) {
  if (list->count >= list->capacity) {
    if (list->capacity >= MAX_CANDIDATES) {
      printf("Reached maximum candidates limit of %d\n", MAX_CANDIDATES);
      return;
    }
    list->capacity *= 2;
    if (list->capacity > MAX_CANDIDATES) list->capacity = MAX_CANDIDATES;
    list->candidates =
      realloc(list->candidates, list->capacity * sizeof(candidate_t));
    for (int i = list->count; i < list->capacity; i++) {
      mpz_init(list->candidates[i].p);
      mpz_init(list->candidates[i].q);
    }
  }

  mpz_set(list->candidates[list->count].p, p);
  mpz_set(list->candidates[list->count].q, q);
  list->count++;
}

void add_candidate_safe(
  candidate_list_t *list, mpz_t p, mpz_t q, pthread_mutex_t *mutex
) {
  pthread_mutex_lock(mutex);

  if (list->count >= list->capacity) {
    if (list->capacity >= MAX_CANDIDATES) {
      printf("Reached maximum candidates limit of %d\n", MAX_CANDIDATES);
      pthread_mutex_unlock(mutex);
      return;
    }
    list->capacity *= 2;
    if (list->capacity > MAX_CANDIDATES) list->capacity = MAX_CANDIDATES;
    list->candidates =
      realloc(list->candidates, list->capacity * sizeof(candidate_t));
    for (int i = list->count; i < list->capacity; i++) {
      mpz_init(list->candidates[i].p);
      mpz_init(list->candidates[i].q);
    }
  }

  mpz_set(list->candidates[list->count].p, p);
  mpz_set(list->candidates[list->count].q, q);
  list->count++;

  pthread_mutex_unlock(mutex);
}

void clear_candidate_list(candidate_list_t *list) {
  for (int i = 0; i < list->capacity; i++) {
    mpz_clear(list->candidates[i].p);
    mpz_clear(list->candidates[i].q);
  }
  free(list->candidates);
  list->count = 0;
}

void reverse_bits(mpz_t result, mpz_t num, int bit_length) {
  mpz_set_ui(result, 0);

  for (int i = 0; i < bit_length; i++)
    if (mpz_tstbit(num, i)) mpz_setbit(result, bit_length - 1 - i);
}

void create_mask(mpz_t mask, int mask_size, int total_bits) {
  mpz_set_ui(mask, 0);

  for (int i = 0; i < mask_size; i++)
    mpz_setbit(mask, total_bits - 1 - i);

  for (int i = 0; i < mask_size; i++)
    mpz_setbit(mask, i);
}

int check_constraints(
  mpz_t p, mpz_t q, mpz_t n, mpz_t veil_xor, int mask_size
) {
  mpz_t p_masked, q_masked, product, q_rev, p_xor_q_rev;
  mpz_t mask, temp, n_masked, veil_masked;

  mpz_init(p_masked);
  mpz_init(q_masked);
  mpz_init(product);
  mpz_init(q_rev);
  mpz_init(p_xor_q_rev);
  mpz_init(mask);
  mpz_init(temp);
  mpz_init(n_masked);
  mpz_init(veil_masked);

  create_mask(mask, mask_size, SIZE);

  mpz_and(p_masked, p, mask);
  mpz_and(q_masked, q, mask);

  // Check multiplication constraint
  mpz_mul(product, p_masked, q_masked);

  // Check LSB bits of product - they must match exactly
  for (int i = 0; i < mask_size; i++)
    if (mpz_tstbit(product, i) != mpz_tstbit(n, i)) goto cleanup_false;

  // Check MSB bits of product with the special constraint
  // Extract top (mask_size + 1) bits of both product and n
  mpz_t top_n, top_product, diff;
  mpz_init(top_n);
  mpz_init(top_product);
  mpz_init(diff);

  // Get top (mask_size + 1) bits of n
  mpz_tdiv_q_2exp(top_n, n, 2 * SIZE - mask_size - 1);
  mpz_tdiv_r_2exp(top_n, top_n, mask_size + 1);

  // Get top (mask_size + 1) bits of product
  mpz_tdiv_q_2exp(top_product, product, 2 * SIZE - mask_size - 1);
  mpz_tdiv_r_2exp(top_product, top_product, mask_size + 1);

  // Check if top_product > top_n
  if (mpz_cmp(top_product, top_n) > 0) {
    mpz_clear(top_n);
    mpz_clear(top_product);
    mpz_clear(diff);
    goto cleanup_false;
  }

  // Check if top_n - top_product > mask_size + 1
  mpz_sub(diff, top_n, top_product);
  if (mpz_cmp_ui(diff, mask_size + 1) > 0) {
    mpz_clear(top_n);
    mpz_clear(top_product);
    mpz_clear(diff);
    goto cleanup_false;
  }

  mpz_clear(top_n);
  mpz_clear(top_product);
  mpz_clear(diff);

  // Check veil XOR constraint
  reverse_bits(q_rev, q_masked, SIZE);
  mpz_xor(p_xor_q_rev, p_masked, q_rev);

  // Apply mask to veil_xor for comparison
  create_mask(temp, mask_size, SIZE);
  mpz_and(veil_masked, veil_xor, temp);
  mpz_and(p_xor_q_rev, p_xor_q_rev, temp);

  if (mpz_cmp(p_xor_q_rev, veil_masked) != 0) goto cleanup_false;

  // Cleanup and return success
  mpz_clear(p_masked);
  mpz_clear(q_masked);
  mpz_clear(product);
  mpz_clear(q_rev);
  mpz_clear(p_xor_q_rev);
  mpz_clear(mask);
  mpz_clear(temp);
  mpz_clear(n_masked);
  mpz_clear(veil_masked);
  return 1;

cleanup_false:
  mpz_clear(p_masked);
  mpz_clear(q_masked);
  mpz_clear(product);
  mpz_clear(q_rev);
  mpz_clear(p_xor_q_rev);
  mpz_clear(mask);
  mpz_clear(temp);
  mpz_clear(n_masked);
  mpz_clear(veil_masked);
  return 0;
}

// Generate new candidates by extending current templates
void generate_candidates(
  candidate_list_t *new_list, mpz_t p_template, mpz_t q_template, int mask_size
) {
  mpz_t new_p, new_q;
  mpz_init(new_p);
  mpz_init(new_q);

  // Try all combinations of new MSB and LSB bits
  for (int p_msb = 0; p_msb <= 1; p_msb++) {
    for (int p_lsb = 0; p_lsb <= 1; p_lsb++) {
      for (int q_msb = 0; q_msb <= 1; q_msb++) {
        for (int q_lsb = 0; q_lsb <= 1; q_lsb++) {
          mpz_set(new_p, p_template);
          mpz_set(new_q, q_template);

          if (p_msb)
            mpz_setbit(new_p, SIZE - mask_size);
          else
            mpz_clrbit(new_p, SIZE - mask_size);

          if (q_msb)
            mpz_setbit(new_q, SIZE - mask_size);
          else
            mpz_clrbit(new_q, SIZE - mask_size);

          if (p_lsb)
            mpz_setbit(new_p, mask_size - 1);
          else
            mpz_clrbit(new_p, mask_size - 1);

          if (q_lsb)
            mpz_setbit(new_q, mask_size - 1);
          else
            mpz_clrbit(new_q, mask_size - 1);

          add_candidate(new_list, new_p, new_q);
        }
      }
    }
  }

  mpz_clear(new_p);
  mpz_clear(new_q);
}

void *thread_worker(void *arg) {
  thread_data_t *data = (thread_data_t *)arg;

  for (int i = data->start_idx;
       i < data->end_idx && i < data->input_candidates->count;
       i++) {
    candidate_list_t temp_candidates;
    init_candidate_list(&temp_candidates);

    generate_candidates(
      &temp_candidates,
      data->input_candidates->candidates[i].p,
      data->input_candidates->candidates[i].q,
      data->mask_size
    );

    for (int j = 0; j < temp_candidates.count; j++) {
      if (check_constraints(
            temp_candidates.candidates[j].p,
            temp_candidates.candidates[j].q,
            data->n,
            data->veil_xor,
            data->mask_size
          )) {
        add_candidate_safe(
          data->output_candidates,
          temp_candidates.candidates[j].p,
          temp_candidates.candidates[j].q,
          data->output_mutex
        );
      }
    }

    clear_candidate_list(&temp_candidates);
  }

  return NULL;
}

// Final verification function to check complete factorization
int verify_complete_factorization(
  candidate_list_t *candidates,
  mpz_t n,
  mpz_t veil_xor,
  mpz_t p_result,
  mpz_t q_result
) {
  printf(
    "Performing final verification of %d candidates...\n", candidates->count
  );

  mpz_t product, q_rev, p_xor_q_rev;
  mpz_init(product);
  mpz_init(q_rev);
  mpz_init(p_xor_q_rev);

  for (int i = 0; i < candidates->count; i++) {
    // Check if p * q = n
    mpz_mul(product, candidates->candidates[i].p, candidates->candidates[i].q);

    if (mpz_cmp(product, n) == 0) {
      // Also verify the veil XOR constraint
      reverse_bits(q_rev, candidates->candidates[i].q, SIZE);
      mpz_xor(p_xor_q_rev, candidates->candidates[i].p, q_rev);

      if (mpz_cmp(p_xor_q_rev, veil_xor) == 0) {
        printf("Found valid complete factorization!\n");
        printf(
          "Candidate %d satisfies both p*q=n and p^reverse(q)=veil_xor\n", i
        );

        mpz_set(p_result, candidates->candidates[i].p);
        mpz_set(q_result, candidates->candidates[i].q);

        mpz_clear(product);
        mpz_clear(q_rev);
        mpz_clear(p_xor_q_rev);
        return 1;
      }
    }
  }

  printf("No candidate satisfies the complete factorization!\n");
  mpz_clear(product);
  mpz_clear(q_rev);
  mpz_clear(p_xor_q_rev);
  return 0;
}

// Progressive factorization algorithm
int progressive_factorization(
  mpz_t p_result, mpz_t q_result, mpz_t n, mpz_t veil_xor
) {
  candidate_list_t valid_candidates, new_candidates;
  mpz_t p_template, q_template;

  init_candidate_list(&valid_candidates);
  init_candidate_list(&new_candidates);
  mpz_init(p_template);
  mpz_init(q_template);

  printf("Starting progressive factorization...\n");
  printf("n has %zu bits\n", mpz_sizeinbase(n, 2));
  printf("veil_xor has %zu bits\n", mpz_sizeinbase(veil_xor, 2));

  for (int i1 = 0; i1 <= 1; i1++) {
    for (int i2 = 0; i2 <= 1; i2++) {
      for (int i3 = 0; i3 <= 1; i3++) {
        for (int i4 = 0; i4 <= 1; i4++) {
          mpz_set_ui(p_template, 0);
          mpz_set_ui(q_template, 0);

          if (i1) mpz_setbit(p_template, SIZE - 1);
          if (i2) mpz_setbit(p_template, 0);
          if (i3) mpz_setbit(q_template, SIZE - 1);
          if (i4) mpz_setbit(q_template, 0);

          if (check_constraints(p_template, q_template, n, veil_xor, 1))
            add_candidate(&valid_candidates, p_template, q_template);
        }
      }
    }
  }

  printf("Starting with %d valid 1-bit candidates\n", valid_candidates.count);

  int num_threads = sysconf(_SC_NPROCESSORS_ONLN);
  printf("Using %d threads\n", num_threads);

  for (int mask_size = 2; mask_size <= SIZE / 2; mask_size++) {
    new_candidates.count = 0;

    if (valid_candidates.count == 0) {
      printf("No more valid candidates found\n");
      break;
    }

    // Don't create more threads than we have candidates
    int actual_threads = (valid_candidates.count < num_threads)
      ? valid_candidates.count
      : num_threads;

    // Create thread data structures
    pthread_t *threads = malloc(actual_threads * sizeof(pthread_t));
    thread_data_t *thread_data = malloc(actual_threads * sizeof(thread_data_t));
    pthread_mutex_t output_mutex = PTHREAD_MUTEX_INITIALIZER;

    // Calculate work distribution
    int candidates_per_thread = valid_candidates.count / actual_threads;
    int remaining_candidates = valid_candidates.count % actual_threads;

    // Launch threads
    int current_start = 0;
    for (int t = 0; t < actual_threads; t++) {
      thread_data[t].thread_id = t;
      thread_data[t].start_idx = current_start;

      // Add one extra candidate to first 'remaining_candidates' threads
      int candidates_for_this_thread =
        candidates_per_thread + (t < remaining_candidates ? 1 : 0);
      thread_data[t].end_idx = current_start + candidates_for_this_thread;
      current_start = thread_data[t].end_idx;

      thread_data[t].input_candidates = &valid_candidates;
      thread_data[t].output_candidates = &new_candidates;
      thread_data[t].mask_size = mask_size;
      thread_data[t].output_mutex = &output_mutex;

      // Debug output for work distribution
      if (mask_size <= 4) { // Only print for early iterations
        printf(
          "Thread %d: processing candidates %d to %d\n",
          t,
          thread_data[t].start_idx,
          thread_data[t].end_idx - 1
        );
      }

      // Initialize mpz_t values for this thread
      mpz_init_set(thread_data[t].n, n);
      mpz_init_set(thread_data[t].veil_xor, veil_xor);

      pthread_create(&threads[t], NULL, thread_worker, &thread_data[t]);
    }

    // Wait for all threads to complete
    for (int t = 0; t < actual_threads; t++) {
      pthread_join(threads[t], NULL);
      mpz_clear(thread_data[t].n);
      mpz_clear(thread_data[t].veil_xor);
    }

    // Cleanup thread resources
    pthread_mutex_destroy(&output_mutex);
    free(threads);
    free(thread_data);

    candidate_list_t temp = valid_candidates;
    valid_candidates = new_candidates;
    new_candidates = temp;
    new_candidates.count = 0;

    printf(
      "After %d bits: %d valid candidates\n", mask_size, valid_candidates.count
    );

    if (valid_candidates.count == 0) {
      printf("No more valid candidates found\n");
      break;
    }

    // Limit candidates to prevent memory explosion
    if (valid_candidates.count > 500000) {
      printf("Too many candidates, keeping first 500000\n");
      valid_candidates.count = 500000;
    }

    // When we reach 512 bits (half of SIZE), perform final verification
    if (mask_size == SIZE / 2) {
      printf(
        "Reached %d bits - performing final complete factorization check...\n",
        mask_size
      );
      if (verify_complete_factorization(
            &valid_candidates, n, veil_xor, p_result, q_result
          )) {
        // Found a valid complete factorization
        clear_candidate_list(&valid_candidates);
        clear_candidate_list(&new_candidates);
        mpz_clear(p_template);
        mpz_clear(q_template);
        return 1;
      } else {
        printf("No complete factorization found at 512 bits. Continuing...\n");
      }
    }
  }

  if (valid_candidates.count == 0) {
    printf("No valid factors found\n");
    clear_candidate_list(&valid_candidates);
    clear_candidate_list(&new_candidates);
    mpz_clear(p_template);
    mpz_clear(q_template);
    return 0;
  }

  // Return the first valid solution
  mpz_set(p_result, valid_candidates.candidates[0].p);
  mpz_set(q_result, valid_candidates.candidates[0].q);

  clear_candidate_list(&valid_candidates);
  clear_candidate_list(&new_candidates);
  mpz_clear(p_template);
  mpz_clear(q_template);
  return 1;
}

// Parse challenge data from out.txt
int parse_challenge_data(mpz_t n, mpz_t c, mpz_t veil_xor) {
  FILE *file = fopen("out.txt", "r");
  if (!file) {
    printf("Error: Could not open out.txt\n");
    return 0;
  }

  char line[4096];
  int n_found = 0, c_found = 0, veil_found = 0;

  while (fgets(line, sizeof(line), file)) {
    if (strncmp(line, "n :", 3) == 0) {
      if (mpz_set_str(n, line + 4, 10) == 0) n_found = 1;
    } else if (strncmp(line, "c :", 3) == 0) {
      if (mpz_set_str(c, line + 4, 10) == 0) c_found = 1;
    } else if (strncmp(line, "Veil XOR:", 9) == 0) {
      if (mpz_set_str(veil_xor, line + 10, 10) == 0) veil_found = 1;
    }
  }

  fclose(file);
  return n_found && c_found && veil_found;
}

// Solve the RSA challenge
int solve_challenge(mpz_t n, mpz_t c, mpz_t veil_xor) {
  mpz_t p, q, phi, d, e, m;
  mpz_init(p);
  mpz_init(q);
  mpz_init(phi);
  mpz_init(d);
  mpz_init(e);
  mpz_init(m);

  printf("Starting progressive factorization...\n");

  if (!progressive_factorization(p, q, n, veil_xor)) {
    printf("Failed to find factors\n");
    goto cleanup;
  }

  printf("Found factors:\n");
  gmp_printf("p = %Zd\n", p);
  gmp_printf("q = %Zd\n", q);

  // Verify the solution
  mpz_t temp, q_rev;
  mpz_init(temp);
  mpz_init(q_rev);

  mpz_mul(temp, p, q);
  if (mpz_cmp(temp, n) != 0) {
    printf("Invalid factorization: p * q != n\n");
    mpz_clear(temp);
    mpz_clear(q_rev);
    goto cleanup;
  }

  reverse_bits(q_rev, q, SIZE);
  mpz_xor(temp, p, q_rev);
  if (mpz_cmp(temp, veil_xor) != 0) {
    printf("Invalid veil XOR: p ^ reverse(q) != veil_xor\n");
    mpz_clear(temp);
    mpz_clear(q_rev);
    goto cleanup;
  }

  printf("Factorization verified!\n");

  // Compute private exponent
  mpz_sub_ui(temp, p, 1);
  mpz_sub_ui(q_rev, q, 1);
  mpz_mul(phi, temp, q_rev);

  mpz_set_ui(e, 65537);
  if (mpz_invert(d, e, phi) == 0) {
    printf("Failed to compute private exponent\n");
    mpz_clear(temp);
    mpz_clear(q_rev);
    goto cleanup;
  }

  // Decrypt
  mpz_powm(m, c, d, n);

  printf("Decrypted message (hex): ");
  mpz_out_str(stdout, 16, m);
  printf("\n");

  // Try to convert to ASCII if reasonable size
  if (mpz_sizeinbase(m, 2) <= 1024) {
    char *flag_str = mpz_get_str(NULL, 16, m);
    printf("Flag (hex): %s\n", flag_str);

    // Convert hex to ASCII
    int len = strlen(flag_str);
    if (len % 2 == 0) {
      printf("Flag (ASCII): ");
      for (int i = 0; i < len; i += 2) {
        char hex_byte[3] = {flag_str[i], flag_str[i + 1], '\0'};
        int byte_val = strtol(hex_byte, NULL, 16);
        if (byte_val >= 32 && byte_val <= 126)
          printf("%c", byte_val);
        else
          printf("\\x%02x", byte_val);
      }
      printf("\n");
    }
    free(flag_str);
  }

  mpz_clear(temp);
  mpz_clear(q_rev);
  mpz_clear(p);
  mpz_clear(q);
  mpz_clear(phi);
  mpz_clear(d);
  mpz_clear(e);
  mpz_clear(m);
  return 1;

cleanup:
  mpz_clear(p);
  mpz_clear(q);
  mpz_clear(phi);
  mpz_clear(d);
  mpz_clear(e);
  mpz_clear(m);
  return 0;
}

int main() {
  mpz_t n, c, veil_xor;
  mpz_init(n);
  mpz_init(c);
  mpz_init(veil_xor);

  printf("=== Veil XOR RSA Solver ===\n\n");

  if (!parse_challenge_data(n, c, veil_xor)) {
    printf("Failed to parse challenge data from out.txt\n");
    goto cleanup;
  }

  printf("Challenge data loaded successfully\n");
  gmp_printf("n = %Zd\n", n);
  gmp_printf("c = %Zd\n", c);
  gmp_printf("veil_xor = %Zd\n", veil_xor);
  printf("\n");

  if (!solve_challenge(n, c, veil_xor)) {
    printf("Failed to solve challenge\n");
    goto cleanup;
  }

  mpz_clear(n);
  mpz_clear(c);
  mpz_clear(veil_xor);
  return 0;

cleanup:
  mpz_clear(n);
  mpz_clear(c);
  mpz_clear(veil_xor);
  return 1;
}
