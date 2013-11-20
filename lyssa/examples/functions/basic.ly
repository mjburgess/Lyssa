

# -> to \n  quote
add (x y) -> x + y

map [1 2] `(x y) -> x

add (x) {
    `(y) {
        x + y
    }
}



 (x)