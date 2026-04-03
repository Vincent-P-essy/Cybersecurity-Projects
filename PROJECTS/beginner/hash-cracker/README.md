```ruby
██╗  ██╗ █████╗ ███████╗██╗  ██╗ ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗
██║  ██║██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║███████╗███████║██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║██╔══██║╚════██║██╔══██║██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║██║  ██║███████║██║  ██║╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

[#  Hash Cracker (C++)

A multi-threaded hash cracking tool I developed to explore practical aspects of cybersecurity, password security, and performance optimization in C++.

This project implements several attack strategies used in real-world scenarios such as dictionary attacks, brute-force, and rule-based mutations.

---

## Features

- Supports multiple hash types: **MD5, SHA1, SHA256, SHA512**
- Automatic hash type detection based on length
- High-performance **multi-threaded engine**
- Dictionary attacks using optimized file handling
- Brute-force mode with configurable charset and max length
- Rule-based mutations:
  - capitalization
  - leet transformations
  - suffix/prefix additions
  - reverse / toggle case
- Salt support (prepend / append)
- Real-time terminal feedback:
  - speed
  - ETA
  - progress bar

---

##  How it works

The program distributes the workload across multiple threads, allowing efficient exploration of large keyspaces.

Different attack modes can be combined:
- Dictionary → fast and realistic
- Rules → expands search space intelligently
- Brute-force → exhaustive fallback

---

##  Example

```bash
./install.sh

hashcracker --hash 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 \
  --wordlist wordlists/10k-most-common.txt