#!/usr/bin/env python3
"""Türk alfabesi sırasını kontrol et"""

alfabe = list("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")

print("Türk Alfabesi (29 harf):")
print("="*50)
for i, harf in enumerate(alfabe, 1):
    print(f"{i:2d}. {harf}")

print(f"\nToplam: {len(alfabe)} harf")
print("\nDoğru sıralama olmalı:")
print("A B C Ç D E F G Ğ H I İ J K L M N O Ö P R S Ş T U Ü V Y Z")
