;; advanced_entities.lsp
;; Advanced shape creation: rectangle, arc, ellipse, mtext, wipeout
;; Enhanced with door and window creation with automatic annotation

(defun c:create-rectangle (x1 y1 x2 y2 layer / p1 p2)
  (setq p1 (list x1 y1 0.0))
  (setq p2 (list x2 y2 0.0))
  (if layer
    (progn
      (ensure_layer_exists layer "white" "CONTINUOUS")
      (set_current_layer layer)
    )
  )
  (command "_RECTANG" p1 p2)
  (princ (strcat "\nRectangle created from (" (rtos x1 2 2) "," (rtos y1 2 2)
                 ") to (" (rtos x2 2 2) "," (rtos y2 2 2) ")"))
)

(defun c:create-arc (cx cy radius startAng endAng layer / center sp ep)
  (setq center (list cx cy 0.0))
  (setq sp (list (+ cx (* radius (cos (* pi (/ startAng 180.0)))))
                 (+ cy (* radius (sin (* pi (/ startAng 180.0)))))
                 0.0))
  (setq ep (list (+ cx (* radius (cos (* pi (/ endAng 180.0)))))
                 (+ cy (* radius (sin (* pi (/ endAng 180.0)))))
                 0.0))
  (if layer
    (progn
      (ensure_layer_exists layer "white" "CONTINUOUS")
      (set_current_layer layer)
    )
  )
  (command "_ARC" "C" center sp ep)
  (princ (strcat "\nArc created at (" (rtos cx 2 2) "," (rtos cy 2 2)
                 ") radius " (rtos radius 2 2)))
)

(defun c:create-ellipse (cx cy major_dx major_dy minor_ratio layer / center major_end)
  (setq center (list cx cy 0.0))
  (setq major_end (list (+ cx major_dx) (+ cy major_dy) 0.0))
  (if layer
    (progn
      (ensure_layer_exists layer "white" "CONTINUOUS")
      (set_current_layer layer)
    )
  )
  (command "_ELLIPSE" center major_end minor_ratio)
  (princ (strcat "\nEllipse created at (" (rtos cx 2 2) "," (rtos cy 2 2) ")"))
)

(defun c:create-mtext (x y width txt height layer style rotation / inspt)
  (setq inspt (list x y 0.0))
  (if layer
    (progn
      (ensure_layer_exists layer "white" "CONTINUOUS")
      (set_current_layer layer)
    )
  )
  (command "_.-MTEXT" inspt "H" height "R" rotation
           (if style (list "S" style) "")
           "W" width "" txt "")
  (princ "\nMText created.")
)

(defun c:create-wipeout-from-points (ptlist frameVisible / )
  (setvar "WIPEOUTFRAME" (if frameVisible 1 0))
  (command "_WIPEOUT" "P")
  (foreach p ptlist (command p))
  (command "")
  (princ "\nWipeout created.")
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; DOOR AND WINDOW CREATION WITH AUTOMATIC ANNOTATION
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Helper function: Ensure annotation layers exist
(defun ensure-annotation-layers ( / )
  (ensure_layer_exists "A-DOOR" "cyan" "CONTINUOUS")
  (ensure_layer_exists "A-DOOR-ANNO" "cyan" "CONTINUOUS")
  (ensure_layer_exists "A-WIND" "blue" "CONTINUOUS")
  (ensure_layer_exists "A-WIND-ANNO" "blue" "CONTINUOUS")
  (ensure_layer_exists "A-ANNO" "yellow" "CONTINUOUS")
)

;; Helper function: Create attribute definition
(defun create-attribute-def (tag prompt default height insertion-pt justification / )
  (command "_ATTDEF"
           ""                    ; No flags (could be "I" for invisible, "C" for constant, "V" for verify)
           tag                   ; Tag name
           prompt                ; Prompt text
           default               ; Default value
           insertion-pt          ; Insertion point
           height                ; Text height
           "0"                   ; Rotation angle
  )
  (princ)
)

;; Helper function: Generate unique reference ID
(defun generate-ref-id (prefix / count ref-id)
  (setq count 1)
  (setq ref-id (strcat prefix (itoa count)))
  (while (tblsearch "BLOCK" ref-id)
    (setq count (1+ count))
    (setq ref-id (strcat prefix (itoa count)))
  )
  ref-id
)

;; Helper function: Create annotation text with leader
(defun create-annotation-leader (start-pt text-pt text-str text-height layer / )
  (if layer
    (progn
      (ensure_layer_exists layer "yellow" "CONTINUOUS")
      (set_current_layer layer)
    )
  )
  ;; Create leader line
  (command "_LINE" start-pt text-pt "")
  ;; Create text annotation
  (command "_TEXT" "J" "L" text-pt text-height "0" text-str)
  (princ)
)

;; Main function: Create door with annotation
;; Parameters: x y width height wall-thickness swing-angle door-type ref-id
;; door-type: "SINGLE", "DOUBLE", "SLIDING", "POCKET"
;; swing-angle: 0, 90, 180, 270 (degrees, direction of swing)
(defun c:create-door (x y width height wall-thickness swing-angle door-type ref-id / 
                      base-pt door-layer anno-layer swing-radius p1 p2 p3 p4
                      arc-start arc-end mid-pt anno-pt anno-text)
  ;; Ensure layers exist
  (ensure-annotation-layers)
  (setq door-layer "A-DOOR")
  (setq anno-layer "A-DOOR-ANNO")
  
  ;; Set current layer
  (set_current_layer door-layer)
  
  ;; Calculate base point and geometry
  (setq base-pt (list x y 0.0))
  (setq swing-radius width)
  
  ;; Generate reference ID if not provided
  (if (not ref-id)
    (setq ref-id (generate-ref-id "D"))
  )
  
  ;; Create door based on type
  (cond
    ;; SINGLE SWING DOOR
    ((= (strcase door-type) "SINGLE")
     (progn
       ;; Draw door frame (opening in wall)
       (setq p1 (list x y 0.0))
       (setq p2 (list (+ x width) y 0.0))
       (command "_LINE" p1 p2 "")
       
       ;; Draw door swing arc
       (cond
         ((= swing-angle 0)    ; Swing right
          (setq arc-start p1)
          (setq arc-end (list (+ x width) (+ y width) 0.0)))
         ((= swing-angle 90)   ; Swing up
          (setq arc-start (list (+ x width) y 0.0))
          (setq arc-end (list (+ x width) (+ y width) 0.0)))
         ((= swing-angle 180)  ; Swing left
          (setq arc-start (list (+ x width) y 0.0))
          (setq arc-end (list x (+ y width) 0.0)))
         ((= swing-angle 270)  ; Swing down
          (setq arc-start p1)
          (setq arc-end (list x (+ y width) 0.0)))
       )
       (command "_ARC" "C" base-pt arc-start arc-end)
       
       ;; Draw door panel line
       (command "_LINE" base-pt arc-end "")
     )
    )
    
    ;; DOUBLE SWING DOOR
    ((= (strcase door-type) "DOUBLE")
     (progn
       (setq mid-pt (list (+ x (/ width 2.0)) y 0.0))
       ;; Draw opening
       (command "_LINE" (list x y 0.0) (list (+ x width) y 0.0) "")
       ;; Left door arc
       (command "_ARC" "C" (list x y 0.0) 
                (list x y 0.0) 
                (list (+ x (/ width 2.0)) (+ y (/ width 2.0)) 0.0))
       ;; Right door arc
       (command "_ARC" "C" (list (+ x width) y 0.0)
                (list (+ x width) y 0.0)
                (list (+ x (/ width 2.0)) (+ y (/ width 2.0)) 0.0))
     )
    )
    
    ;; SLIDING DOOR
    ((= (strcase door-type) "SLIDING")
     (progn
       ;; Draw track
       (command "_LINE" (list x y 0.0) (list (+ x width) y 0.0) "")
       ;; Draw door panel(s)
       (setq p1 (list (+ x (* width 0.25)) (+ y (* height 0.1)) 0.0))
       (setq p2 (list (+ x (* width 0.75)) (+ y (* height 0.9)) 0.0))
       (command "_RECTANG" p1 p2)
     )
    )
    
    ;; POCKET DOOR
    ((= (strcase door-type) "POCKET")
     (progn
       ;; Draw opening
       (command "_LINE" (list x y 0.0) (list (+ x width) y 0.0) "")
       ;; Draw pocket indication (dashed line)
       (command "_LINE" 
                (list (+ x width) y 0.0) 
                (list (+ x width) (+ y height) 0.0) "")
       ;; Draw door panel in pocket
       (setq p1 (list (+ x width 5) (+ y (* height 0.1)) 0.0))
       (setq p2 (list (+ x width 10) (+ y (* height 0.9)) 0.0))
       (command "_RECTANG" p1 p2)
     )
    )
  )
  
  ;; Create annotation
  (setq anno-pt (list (+ x (/ width 2.0)) (+ y height 20.0) 0.0))
  (setq anno-text (strcat ref-id 
                          "\\P" door-type " DOOR"
                          "\\P" (rtos width 2 0) "mm x " (rtos height 2 0) "mm"))
  
  ;; Create leader and annotation
  (set_current_layer anno-layer)
  (create-annotation-leader 
    (list (+ x (/ width 2.0)) y 0.0)
    anno-pt
    anno-text
    2.5
    anno-layer
  )
  
  ;; Return to original layer
  (princ (strcat "\n" door-type " door created: " ref-id 
                 " (" (rtos width 2 0) "mm x " (rtos height 2 0) "mm)"))
  (princ)
)

;; Main function: Create window with annotation
;; Parameters: x y width height sill-height window-type glass-type ref-id
;; window-type: "FIXED", "CASEMENT", "SLIDING", "DOUBLE-HUNG", "AWNING"
;; glass-type: "SINGLE", "DOUBLE", "TRIPLE", "TEMPERED"
(defun c:create-window (x y width height sill-height window-type glass-type ref-id /
                        base-pt window-layer anno-layer p1 p2 p3 p4 
                        frame-offset glass-offset anno-pt anno-text mid-x mid-y)
  ;; Ensure layers exist
  (ensure-annotation-layers)
  (setq window-layer "A-WIND")
  (setq anno-layer "A-WIND-ANNO")
  
  ;; Set current layer
  (set_current_layer window-layer)
  
  ;; Calculate base point and offsets
  (setq base-pt (list x y 0.0))
  (setq frame-offset 5.0)
  (setq glass-offset 10.0)
  
  ;; Generate reference ID if not provided
  (if (not ref-id)
    (setq ref-id (generate-ref-id "W"))
  )
  
  ;; Create window based on type
  (cond
    ;; FIXED WINDOW
    ((= (strcase window-type) "FIXED")
     (progn
       ;; Outer frame
       (setq p1 (list x y 0.0))
       (setq p2 (list (+ x width) (+ y height) 0.0))
       (command "_RECTANG" p1 p2)
       
       ;; Inner glass area
       (setq p3 (list (+ x glass-offset) (+ y glass-offset) 0.0))
       (setq p4 (list (+ x (- width glass-offset)) (+ y (- height glass-offset)) 0.0))
       (command "_RECTANG" p3 p4)
       
       ;; Cross lines for glass indication
       (command "_LINE" p3 p4 "")
       (command "_LINE" 
                (list (+ x glass-offset) (+ y (- height glass-offset)) 0.0)
                (list (+ x (- width glass-offset)) (+ y glass-offset) 0.0) "")
     )
    )
    
    ;; CASEMENT WINDOW
    ((= (strcase window-type) "CASEMENT")
     (progn
       ;; Frame
       (command "_RECTANG" (list x y 0.0) (list (+ x width) (+ y height) 0.0))
       ;; Glass pane
       (setq p3 (list (+ x glass-offset) (+ y glass-offset) 0.0))
       (setq p4 (list (+ x (- width glass-offset)) (+ y (- height glass-offset)) 0.0))
       (command "_RECTANG" p3 p4)
       ;; Swing indication (small arc)
       (setq mid-x (+ x (/ width 2.0)))
       (setq mid-y (+ y (/ height 2.0)))
       (command "_ARC" "C" (list x mid-y 0.0) 
                (list x mid-y 0.0)
                (list (+ x (* width 0.3)) mid-y 0.0))
     )
    )
    
    ;; SLIDING WINDOW
    ((= (strcase window-type) "SLIDING")
     (progn
       ;; Outer frame
       (command "_RECTANG" (list x y 0.0) (list (+ x width) (+ y height) 0.0))
       ;; Divider
       (setq mid-x (+ x (/ width 2.0)))
       (command "_LINE" (list mid-x y 0.0) (list mid-x (+ y height) 0.0) "")
       ;; Glass panes with offset
       (command "_RECTANG" 
                (list (+ x glass-offset) (+ y glass-offset) 0.0)
                (list (- mid-x 2.0) (+ y (- height glass-offset)) 0.0))
       (command "_RECTANG" 
                (list (+ mid-x 2.0) (+ y glass-offset) 0.0)
                (list (+ x (- width glass-offset)) (+ y (- height glass-offset)) 0.0))
     )
    )
    
    ;; DOUBLE-HUNG WINDOW
    ((= (strcase window-type) "DOUBLE-HUNG")
     (progn
       ;; Outer frame
       (command "_RECTANG" (list x y 0.0) (list (+ x width) (+ y height) 0.0))
       ;; Horizontal divider
       (setq mid-y (+ y (/ height 2.0)))
       (command "_LINE" (list x mid-y 0.0) (list (+ x width) mid-y 0.0) "")
       ;; Glass panes
       (command "_RECTANG"
                (list (+ x glass-offset) (+ y glass-offset) 0.0)
                (list (+ x (- width glass-offset)) (- mid-y 2.0) 0.0))
       (command "_RECTANG"
                (list (+ x glass-offset) (+ mid-y 2.0) 0.0)
                (list (+ x (- width glass-offset)) (+ y (- height glass-offset)) 0.0))
     )
    )
    
    ;; AWNING WINDOW
    ((= (strcase window-type) "AWNING")
     (progn
       ;; Frame
       (command "_RECTANG" (list x y 0.0) (list (+ x width) (+ y height) 0.0))
       ;; Glass pane
       (command "_RECTANG"
                (list (+ x glass-offset) (+ y glass-offset) 0.0)
                (list (+ x (- width glass-offset)) (+ y (- height glass-offset)) 0.0))
       ;; Awning hinge line at top
       (command "_LINE" 
                (list (+ x glass-offset) (+ y (- height glass-offset)) 0.0)
                (list (+ x (- width glass-offset)) (+ y (- height glass-offset)) 0.0) "")
     )
    )
  )
  
  ;; Create annotation with comprehensive information
  (setq anno-pt (list (+ x (/ width 2.0)) (+ y height 25.0) 0.0))
  (setq anno-text (strcat ref-id
                          "\\P" window-type " WINDOW"
                          "\\P" (rtos width 2 0) "mm x " (rtos height 2 0) "mm"
                          "\\PSill: " (rtos sill-height 2 0) "mm"
                          "\\PGlass: " glass-type))
  
  ;; Create leader and annotation
  (set_current_layer anno-layer)
  (create-annotation-leader
    (list (+ x (/ width 2.0)) (+ y height) 0.0)
    anno-pt
    anno-text
    2.5
    anno-layer
  )
  
  ;; Return to original layer
  (princ (strcat "\n" window-type " window created: " ref-id
                 " (" (rtos width 2 0) "mm x " (rtos height 2 0) "mm)"
                 " - Sill: " (rtos sill-height 2 0) "mm"))
  (princ)
)

;; Simplified wrapper functions for common door and window types

;; Create standard single swing door
(defun c:create-door-single (x y width height ref-id / )
  (c:create-door x y width height 100 90 "SINGLE" ref-id)
)

;; Create standard double swing door
(defun c:create-door-double (x y width height ref-id / )
  (c:create-door x y width height 100 90 "DOUBLE" ref-id)
)

;; Create standard sliding door
(defun c:create-door-sliding (x y width height ref-id / )
  (c:create-door x y width height 100 0 "SLIDING" ref-id)
)

;; Create standard fixed window
(defun c:create-window-fixed (x y width height sill-height ref-id / )
  (c:create-window x y width height sill-height "FIXED" "DOUBLE" ref-id)
)

;; Create standard casement window
(defun c:create-window-casement (x y width height sill-height ref-id / )
  (c:create-window x y width height sill-height "CASEMENT" "DOUBLE" ref-id)
)

;; Create standard sliding window
(defun c:create-window-sliding (x y width height sill-height ref-id / )
  (c:create-window x y width height sill-height "SLIDING" "DOUBLE" ref-id)
)

(princ "\nAdvanced entity creation loaded.")
(princ "\nDoor and window creation with annotation loaded.")
(princ "\nCommands: CREATE-DOOR, CREATE-WINDOW")
(princ "\nSimplified commands: CREATE-DOOR-SINGLE, CREATE-DOOR-DOUBLE, CREATE-DOOR-SLIDING")
(princ "\n                     CREATE-WINDOW-FIXED, CREATE-WINDOW-CASEMENT, CREATE-WINDOW-SLIDING")
(princ)
