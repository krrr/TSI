;;; The turtle star example from document
(load-ext "turtleext")

(color "red" "yellow")

(define (loop)
  (forward 200)
  (left 170)
  (if (>= (vec2d_abs (pos)) 1)
    (loop)))

(speed 0)
(begin_fill)
(loop)
(end_fill)

(hideturtle)
(exitonclick)