elos = [1780,1701,1650,1565,1435,1135]
sum = 0
for i in range (6):
    for j in range (6):
        if i != j:
            sum += abs(elos[i] - elos[j])
print(sum/30)