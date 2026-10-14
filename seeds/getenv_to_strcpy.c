char *source() {
    char *src = getenv("HOME");
    return src;
}
 
char *sink(char *s) {
    char buf[16]; 
    strcpy(buf, s); 
    return s;
}

char *flow_int() {
    return sink(source());
}

char *flow() { return flow_int(); }