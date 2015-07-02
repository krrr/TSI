(define (abs x)
  (if (< x 0) (- x) x))

;;; pair/list procedures
; accumulate and related ones are taken from SICP exercise 2.33
(define (accumulate op initial sequence)
  (if (null? sequence)
      initial
      (op (car sequence)
          (accumulate op initial (cdr sequence)))))

(define fold-right accumulate)

(define (fold-left op initial seq)
  (if (null? seq)
      initial
      (fold-left op
                 (op initial (car seq))
                 (cdr seq))))

(define (filter predicate sequence)
  (cond ((null? sequence) '())
        ((predicate (car sequence))
         (cons (car sequence)
               (filter predicate (cdr sequence))))
        (else (filter predicate (cdr sequence)))))

(define (map p sequence)
  (accumulate (lambda (x y) (cons (p x) y)) '() sequence))

(define (for-each p sequence)
  (cond ((null? sequence) '())
        (else
         (p (car sequence))
         (for-each p (cdr sequence)))))

(define (append seq1 seq2) (accumulate cons seq2 seq1))

(define (list-ref sequence n)
  (if (= 0)
      (car sequence)
      (list-ref (cdr sequence) (- n 1))))

(define (length sequence)
  (accumulate (lambda (x y) (+ y 1)) 0 sequence))

; car/cdr shortcuts
(define (cadr pair) (car (cdr pair)))
(define (caddr pair) (car (cdr (cdr pair))))
(define (cadddr pair) (car (cdr (cdr (cdr pair)))))
(define (cddr pair) (cdr (cdr pair)))
(define (cdddr pair) (cdr (cdr (cdr pair))))
(define (cddddr pair) (cdr (cdr (cdr pair))))
(define (caadr pair) (car (car (cdr pair))))
(define (cdadr pair) (cdr (car (cdr pair))))

