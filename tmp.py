from Levenshtein import distance
from readmdict import MDX

def calculate_levenshtein_distance(text1, text2):
    m, n = len(text1), len(text2)
    dp = []
    # dp = np.zeros((m + 1, n + 1))
    for i in range(m + 1):
        dp.append([])
        for j in range(n + 1):
            dp[i].append(0)

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

    return dp[m][n]


a = {}
text = '' # 5

headwords = [*MDX('./dicts/Oxford Dictionary of English 2nd.mdx')]
items = [*MDX('./dicts/Oxford Dictionary of English 2nd.mdx').items()]

for headword in headwords:
    headword = headword.decode('utf-8')
    # sim = calculate_levenshtein_distance(text, headword)
    sim = distance(text, headword)
    if len(a) < 10:
        a[headword] = sim
    else:
        a = dict(sorted(a.items(), key=lambda item: item[1]))
        del a[list(a.keys())[-1]]
        a[headword] = sim


print(a)