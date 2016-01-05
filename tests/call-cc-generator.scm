; this example comes from wikipedia page of call/cc

; make a generator that generate every element of lst untouched
(define (gen lst)
  (define (control-state return)
    (for-each (lambda (i)
      ; The next call to (call/cc control-state) will resume
      ; with a newly obtained continuation (outside the gen proc),
      ; so we set return to it. For Racket it's unnecessary, which
      ; is unusual.
      (set! return
        (call/cc (lambda (cont)
          (set! control-state cont)
          (return i)))))
    lst)
    (return 'you-fell-off-the-end))
 
  ; make a closure that holds the control-state
  (lambda () (call/cc control-state)))


;(define g (gen '(1 2 3)))

;(print "generator created")
;(print (g))
;(print (g))
;(print (g))
;(print (g))
;(print (g))
