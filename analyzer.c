#include <stdio.h>
#include <string.h>

/* Basic document word-overlap analyzer using beginner-level string.h functions.
   Functions used: strlen(), strcpy(), strcmp(), strtok().
   Usage: analyzer file1.txt file2.txt */

int main(int argc, char *argv[]) {
    FILE *f1, *f2;
    char text1[10001], text2[10001];
    char words1[1000][100];
    char *word;
    int total = 0, matched = 0;
    int i, found;
    size_t n1, n2;

    if (argc != 3) {
        printf("Usage: analyzer file1.txt file2.txt\n");
        return 1;
    }

    f1 = fopen(argv[1], "rb");
    f2 = fopen(argv[2], "rb");

    if (f1 == NULL || f2 == NULL) {
        if (f1 != NULL) {
            fclose(f1);
        }
        if (f2 != NULL) {
            fclose(f2);
        }
        printf("Error opening input files.\n");
        return 1;
    }

    n1 = fread(text1, 1, sizeof(text1) - 1, f1);
    n2 = fread(text2, 1, sizeof(text2) - 1, f2);
    text1[n1] = '\0';
    text2[n2] = '\0';

    fclose(f1);
    fclose(f2);

    /* Split Document 1 into words using strtok(). */
    word = strtok(text1, " \n\t\r.,!?;:()\"'");
    while (word != NULL && total < 1000) {
        if (strlen(word) < sizeof(words1[0])) {
            strcpy(words1[total], word);
            total++;
        }
        word = strtok(NULL, " \n\t\r.,!?;:()\"'");
    }

    /* Compare words from Document 2 with Document 1 using strcmp(). */
    word = strtok(text2, " \n\t\r.,!?;:()\"'");
    while (word != NULL) {
        if (strlen(word) < 100) {
            found = 0;

            for (i = 0; i < total; i++) {
                if (strcmp(words1[i], word) == 0) {
                    found = 1;
                    break;
                }
            }

            if (found == 1) {
                matched++;
            }
        }

        word = strtok(NULL, " \n\t\r.,!?;:()\"'");
    }

    if (total > 0) {
        double similarity = (matched * 100.0) / total;

        /* Keep displayed percentage within 0 to 100. */
        if (similarity > 100.0) {
            similarity = 100.0;
        }

        printf("Similarity: %.2f%%\n", similarity);
    } else {
        printf("Similarity: 0.00%%\n");
    }

    printf("MATCHED=%d TOTAL=%d\n", matched, total);
    return 0;
}
