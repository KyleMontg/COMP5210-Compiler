int main(void) {
    int value = 1;
    {
        int value = 2;
        {
            int value = 3;
            value = value + 1;
        }
    }
    return value;
}
