int main(void) {
    int mask = 0x0F;
    int value = 0xF0;
    int result = (mask & value) | (mask << 2);
    result ^= 0xAA;
    result = ~result;
    return result;
}
