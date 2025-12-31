#!/usr/bin/env python3

with open('quiny', 'rb') as f:
    data = f.read()

# Create the full palindrome: Data + Reverse(Data)
palindrome = data + data[:-1][::-1]

# Save the final executable
with open('quinindrome', 'wb') as f:
    f.write(palindrome)

print(f'Created quinindrome! Size: {len(palindrome)} bytes')
