(define (println a) (display a) (newline))

; this example is from wikipedia page of call/cc

; make a generator that generate eveny element of lst un touched
(define (gen lst)
  (define (control-state return)
    (for-each 
     (lambda (element)
       ; The next call to (call/cc control-state) will resume
       ; with a newly obtained continuation (outside the gen proc),
       ; so we set return to it. For Racket it's unnecessary, which
       ; is unusual.
       (set! return
         (call/cc (lambda (cont)
           (set! control-state cont)
           (return element)))))
     lst)
    (return 'you-fell-off-the-end))
 
  ; make a closure that holds all status
  (lambda () (call/cc control-state)))


;(define g (gen '(1 2 3)))
;(println "generator created")
;(println (g))
;(println (g))
;(println (g))
;(println (g))
;(println (g))
