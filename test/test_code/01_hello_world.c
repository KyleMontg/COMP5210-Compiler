int main() {
    int x = 10;
    int y = 2;
    int z = 2 + 3;
    int a = z + z + x;
    if(x < y){
        int y = 2;
    }
    for(int i = 0; i < x; i++){
        x += y;
    }
    if(y == x){
        return y;
    }
    return x;
}