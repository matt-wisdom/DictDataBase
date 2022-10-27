#include <stdio.h>
#include <string.h>

int square(int i) {
	return i * i;
}


int seek_index_through_value(char* data, int index) {
    // def seek_index_through_value(data: str, index: int) -> int:
    // 	skip_next, in_str, list_depth, dict_depth = False, False, 0, 0
    // 	for i in range(index, len(data)):
    // 		if skip_next:
    // 			skip_next = False
    // 			continue
    // 		current = data[i]
    // 		if current == "\\":
    // 			skip_next = True
    // 			continue
    // 		if current == '"':
    // 			in_str = not in_str
    // 		if in_str or current == " ":
    // 			continue
    // 		if current == "[":
    // 			list_depth += 1
    // 		elif current == "]":
    // 			list_depth -= 1
    // 		elif current == "{":
    // 			dict_depth += 1
    // 		elif current == "}":
    // 			dict_depth -= 1
    // 		if list_depth == 0 and dict_depth == 0:
    // 			return i + 1
    // The above is the python implementation. Here is the exact same code but written in C
    int skip_next = 0, in_str = 0, list_depth = 0, dict_depth = 0;
    for (int i = index; i < strlen(data); i++) {
        if (skip_next) {
            skip_next = 0;
            continue;
        }
        char current = data[i];
        if (current == '\\') {
            skip_next = 1;
            continue;
        }
        if (current == '"') {
            in_str = !in_str;
        }
        if (in_str || current == ' ') {
            continue;
        }
        if (current == '[') {
            list_depth++;
        } else if (current == ']') {
            list_depth--;
        } else if (current == '{') {
            dict_depth++;
        } else if (current == '}') {
            dict_depth--;
        }
        if (list_depth == 0 && dict_depth == 0) {
            printf("Found index is %c\n", data[i]);
            return i + 1;
        }
    }
}
