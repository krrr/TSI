;;; from http://inst.eecs.berkeley.edu/~cs61a/fa12/projects/proj04/scheme.html
(load-ext "turtleext")

(define sqrt-of-3 1.73205080)  ; too lazy to have a real sqrt

(define (hax-cell pos d)  ; draw cell at pos, and let here be its center
  (let ((center pos)
        (saved-heading (heading)))
    (penup)
    (setpos (- (car center) (/ d 2))
            (- (cdr center) (* d sqrt-of-3 0.5)))
    (setheading 270)
    (pendown)
    (define (loop n)
      (if (> n 0) (begin
        (right 60)
        (forward d)
        (loop (- n 1)))))
    (loop 6)
    (penup)
    (setpos center)
    (setheading saved-heading)
    (pendown)))

(define (hax d depth)
  (let ((curt-x (car (pos)))
        (curt-y (cdr (pos)))
        (half-d (/ d 2)))
    (define sub-hax-poses (list (cons (- curt-x (/ d 4)) (+ curt-y (* d sqrt-of-3 0.25)))
                                (cons (+ curt-x (/ d 2)) curt-y)
                                (cons (- curt-x (/ d 4)) (- curt-y (* d sqrt-of-3 0.25)))))
    (for-each (lambda (p) (hax-cell p half-d)) sub-hax-poses)
    (if (> depth 1)
      (for-each
        (lambda (p)
          (penup)
          (setpos p)
          (pendown)
          (hax half-d (- depth 1)))
        sub-hax-poses))))

(speed 10)
(hax-cell (pos) 250)  ; draw out-most cell
(hax 250 5)
(hideturtle)
(exitonclick)
