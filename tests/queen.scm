(define (enumerate-interval low high)
  (if (> low high)
      '()
      (cons low (enumerate-interval (+ low 1) high))))


(define (flatmap proc seq)
  (accumulate append '() (map proc seq)))

(define (unique-pairs n)
  (flatmap (lambda (i)
             (map (lambda (j) (list i j))
                  (enumerate-interval 1 (- i 1))))
           (enumerate-interval 1 n)))

(define (prine-sum-pairs n)  ; I'm lazy, this isn't runable.
  (map make-sum-pairs
       (filter prime-sum?
               (unique-pairs n))))


; EX 2.41
(define (unique-lists n)
  (flatmap (lambda (i)
             (flatmap (lambda (j)
                      (map (lambda (k) (list i j k))
                           (enumerate-interval 1 (- j 1))))
                      (enumerate-interval 1 (- i 1))))
           (enumerate-interval 1 n)))
(define (s-sum-lists n s)
  (filter (lambda (l) (= s (+ (car l) (cadr l) (caddr l))))
          (unique-lists n)))

;(display (unique-lists 4))
;(newline)
;(display (s-sum-lists 4 6))

; above is from Ex2.40, for filter, flatmap, enumerate-interval

(define empty-board '())

(define (adjoin-position new-row k rest-of-queens)  ; k starts from 1
  (cons new-row rest-of-queens))

(define (safe? k positions)
  (define (check-each i lst dif)
    (if (null? lst)
        #t
        (let ((another-row (car lst)))
          (if (and (not (= i (car lst)))
                   (not (or (= i (+ another-row dif))
                            (= i (- another-row dif)))))
              (check-each i (cdr lst) (+ dif 1))
              #f))))
  (if (> k 1)
      (let ((row-k-1 (cadr positions))
            (row-k   (car positions)))
        (and (or (> row-k (+ row-k-1 1)) (< row-k (- row-k-1 1)))
             (check-each row-k (cdr positions) 1)))
      #t))

(define (queens board-size)
  ; return a list of lists like (1 4 1 4),
  (define (queen-cols k)
    (if (= k 0)
        (list empty-board)
        (filter (lambda (positions) (safe? k positions))
                (flatmap
                 (lambda (rest-of-queens)
                   (map (lambda (new-row)
                          (adjoin-position new-row k rest-of-queens))
                        (enumerate-interval 1 board-size)))
                 (queen-cols (- k 1))))))
  (queen-cols board-size))

(define (queens-louis board-size)
  ; return a list of lists like (1 4 1 4),
  (define (queen-cols k)
    (if (= k 0)
        (list empty-board)
        (filter (lambda (positions) (safe? k positions))
                (flatmap
                 (lambda (new-row)
                   (map (lambda (rest-of-queens)
                          (adjoin-position new-row k rest-of-queens))
                        (queen-cols (- k 1))))
                 (enumerate-interval 1 board-size)))))
  (queen-cols board-size))


;(display (queens 4))
