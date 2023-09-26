letter = "A"
dterm = "Å"
specialFirstLetters = ["A", "Ǻ", "Å", "Ă", "Â", "À", "Á"]
flag1 = letter in specialFirstLetters
print(flag1)
flag2 = dterm in specialFirstLetters
print(flag2)
specialFirstLetterWorkaround = not (flag1 and flag2)
print(specialFirstLetterWorkaround)