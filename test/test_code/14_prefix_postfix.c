int main(void) {
    int x = 1;
    int y = ++x;
    int z = x++;
    return y + z + x;
}
