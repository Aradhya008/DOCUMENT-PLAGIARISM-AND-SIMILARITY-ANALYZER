#include <stdio.h>
#include <string.h>

int main(void)
{
    char doc1[5001], doc2[5001];
    char words1[500][50], words2[500][50];
    int count1 = 0, count2 = 0;
    int i, j, k, found, matched = 0;

    /* Python sends each document as one line. */
    if (fgets(doc1, sizeof(doc1), stdin) == NULL) return 1;
    if (fgets(doc2, sizeof(doc2), stdin) == NULL) return 1;

    /* Split document 1 into words using a simple loop. */
    i = 0;
    while (doc1[i] != '\0' && count1 < 500) {
        while (doc1[i] == ' ' || doc1[i] == '\t' || doc1[i] == '\n' || doc1[i] == ',' || doc1[i] == '.' || doc1[i] == '!' || doc1[i] == '?' || doc1[i] == ';' || doc1[i] == ':') i++;
        if (doc1[i] == '\0') break;
        j = 0;
        while (doc1[i] != '\0' && doc1[i] != ' ' && doc1[i] != '\t' && doc1[i] != '\n' && doc1[i] != ',' && doc1[i] != '.' && doc1[i] != '!' && doc1[i] != '?' && doc1[i] != ';' && doc1[i] != ':') {
            if (j < 49) words1[count1][j++] = doc1[i];
            i++;
        }
        words1[count1][j] = '\0';
        if (j > 0) count1++;
    }

    /* Split document 2 into words using the same loop. */
    i = 0;
    while (doc2[i] != '\0' && count2 < 500) {
        while (doc2[i] == ' ' || doc2[i] == '\t' || doc2[i] == '\n' || doc2[i] == ',' || doc2[i] == '.' || doc2[i] == '!' || doc2[i] == '?' || doc2[i] == ';' || doc2[i] == ':') i++;
        if (doc2[i] == '\0') break;
        j = 0;
        while (doc2[i] != '\0' && doc2[i] != ' ' && doc2[i] != '\t' && doc2[i] != '\n' && doc2[i] != ',' && doc2[i] != '.' && doc2[i] != '!' && doc2[i] != '?' && doc2[i] != ';' && doc2[i] != ':') {
            if (j < 49) words2[count2][j++] = doc2[i];
            i++;
        }
        words2[count2][j] = '\0';
        if (j > 0) count2++;
    }

    /* Count each word in document 2 that also appears in document 1. */
    for (i = 0; i < count2; i++) {
        found = 0;
        for (j = 0; j < count1; j++) {
            if (strcmp(words2[i], words1[j]) == 0) {
                found = 1;
                break;
            }
        }
        if (found == 1) matched++;
    }

    printf("MATCHED=%d TOTAL=%d\n", matched, count2);
    if (count2 > 0) printf("Similarity: %.2f%%\n", matched * 100.0 / count2);
    else printf("Similarity: 0.00%%\n");
    return 0;
}
