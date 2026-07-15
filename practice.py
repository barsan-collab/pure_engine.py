# Program to check if a number is prime or not

num = int(input("enter the number: "))


flag = False

if num == 0 or num == 1:
    print(num, "is not a prime number")
elif num > 1:
    # check for factors
    for i in range(2, num):
        if (num % i) == 0:
            # if factor is found, set flag to True
            flag = True
            # break out of loop
            break

    # check if flag is True
    if flag:
        print(num, "is not a prime number")
    else:
        print(num, "is a prime number")
        
        
#factorial check 
def calculate_factorial(n):
    # Factorial is not defined for negative numbers
    if n < 0:
        return "Factorial is not defined for negative numbers."
    
    result = 1
    
    # Loop from 1 to n (inclusive)
    for i in range(1, n + 1):
        result *= i  # Equivalent to result = result * i
        
    return result

# Example usage:
num = 5
print(f"The factorial of {num} is {calculate_factorial(num)}")
# Output: The factorial of 5 is 120
