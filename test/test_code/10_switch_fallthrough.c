int test(int value) {
    int result = 0;
    switch (value) {
        case 1:
        case 2:
            result = value;
            break;
        case 3:
            result = 9;
            break;
        default:
            result = -1;
    }
    return result;
}
