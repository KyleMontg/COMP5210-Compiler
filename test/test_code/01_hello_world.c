
void main() {
    int x = 1;
    int y = 2 + x;
    int a = x;
    int b = a % y;
    int c = 3 + 2 + 5 + 9 * 2 / 5;
    int d = c + x;
    while(y < 10){
        y++;
    }
    for(int i = 0; i < 10; i++){
        y += i;
    }
    if(y > x ){
      b = x;
    }
    return 0;
}