;; Architectural tools for AutoCAD MCP Server
;; Specialized functions for architectural floor planning

;; Load core functions first
(load "core_functions.lsp")

;; Default architectural settings
(setq *default-wall-thickness* 6.0)
(setq *default-wall-height* 96.0)
(setq *default-door-width* 36.0)
(setq *default-door-height* 84.0)
(setq *default-window-width* 48.0)
(setq *default-window-height* 36.0)
(setq *default-window-sill* 30.0)

;; Function to create architectural wall
(defun create-architectural-wall (start-pt end-pt thickness height / wall-vector wall-angle offset-pt1 offset-pt2)
  "Create an architectural wall with proper thickness"
  (setq wall-vector (mapcar '- end-pt start-pt))
  (setq wall-angle (angle start-pt end-pt))
  (setq offset-angle (+ wall-angle (/ pi 2)))
  
  ;; Calculate offset points for wall thickness
  (setq offset-pt1 (polar start-pt offset-angle (/ thickness 2)))
  (setq offset-pt2 (polar end-pt offset-angle (/ thickness 2)))
  (setq offset-pt3 (polar end-pt offset-angle (- 0 (/ thickness 2))))
  (setq offset-pt4 (polar start-pt offset-angle (- 0 (/ thickness 2))))
  
  ;; Create wall as closed polyline
  (ensure-layer "WALLS" 1 "Continuous" 0.35)
  (set-current-layer "WALLS")
  
  (command "._PLINE" offset-pt1 offset-pt2 offset-pt3 offset-pt4 "C")
  
  ;; Add centerline
  (ensure-layer "WALL-CENTER" 8 "CENTER" 0.15)
  (set-current-layer "WALL-CENTER")
  (draw-line start-pt end-pt)
  
  (display-message "Architectural wall created")
)

;; Function to create door opening with swing
(defun create-door-opening (wall-start wall-end position width height swing-dir / door-angle door-start door-end)
  "Create door opening with swing indication"
  (setq door-angle (angle wall-start wall-end))
  (setq door-start position)
  (setq door-end (polar position door-angle width))
  
  ;; Create door opening
  (ensure-layer "DOORS" 3 "Continuous" 0.25)
  (set-current-layer "DOORS")
  
  ;; Draw door opening lines
  (draw-line door-start door-end)
  
  ;; Draw door swing arc
  (cond
    ((= swing-dir "LEFT_IN")
     (draw-arc door-start 0 (/ pi 2) width))
    ((= swing-dir "LEFT_OUT") 
     (draw-arc door-start pi (+ pi (/ pi 2)) width))
    ((= swing-dir "RIGHT_IN")
     (draw-arc door-end (/ pi 2) pi width))
    ((= swing-dir "RIGHT_OUT")
     (draw-arc door-end (+ pi (/ pi 2)) (* 2 pi) width))
  )
  
  ;; Add door symbol (rectangle representing door)
  (setq door-thickness 2)
  (setq perp-angle (+ door-angle (/ pi 2)))
  (setq door-corner1 (polar door-start perp-angle door-thickness))
  (setq door-corner2 (polar door-end perp-angle door-thickness))
  
  (draw-line door-start door-corner1)
  (draw-line door-corner1 door-corner2)
  (draw-line door-corner2 door-end)
  
  (display-message "Door opening created")
)

;; Function to create window opening
(defun create-window-opening (wall-start wall-end position width height sill-height / win-angle win-start win-end win-sill-start win-sill-end win-head-start win-head-end)
  "Create window opening with sill and header"
  (setq win-angle (angle wall-start wall-end))
  (setq win-start position)
  (setq win-end (polar position win-angle width))
  
  ;; Calculate sill and header positions
  (setq perp-angle (+ win-angle (/ pi 2)))
  (setq win-sill-start (polar win-start perp-angle sill-height))
  (setq win-sill-end (polar win-end perp-angle sill-height))
  (setq win-head-start (polar win-sill-start perp-angle height))
  (setq win-head-end (polar win-sill-end perp-angle height))
  
  ;; Create window layer and draw
  (ensure-layer "WINDOWS" 4 "Continuous" 0.25)
  (set-current-layer "WINDOWS")
  
  ;; Draw window opening rectangle
  (draw-rectangle win-sill-start win-head-end)
  
  ;; Draw window mullions (cross pattern)
  (draw-line (list (/ (+ (car win-sill-start) (car win-sill-end)) 2) 
                   (cadr win-sill-start))
             (list (/ (+ (car win-head-start) (car win-head-end)) 2) 
                   (cadr win-head-start)))
  
  (draw-line (list (car win-sill-start) 
                   (/ (+ (cadr win-sill-start) (cadr win-head-start)) 2))
             (list (car win-sill-end) 
                   (/ (+ (cadr win-sill-end) (cadr win-head-end)) 2)))
  
  ;; Add sill line
  (ensure-layer "WINDOW-SILL" 6 "Continuous" 0.15)
  (set-current-layer "WINDOW-SILL")
  (draw-line win-sill-start win-sill-end)
  
  (display-message "Window opening created")
)

;; Function to create room boundary
(defun create-room-boundary (points room-name / area-val)
  "Create room boundary with area calculation"
  (ensure-layer "ROOMS" 2 "PHANTOM" 0.15)
  (set-current-layer "ROOMS")
  
  ;; Draw room boundary
  (draw-polyline points T)
  
  ;; Calculate and display area
  (setq area-val (polygon-area points))
  
  ;; Add room label at centroid
  (setq centroid (calculate-centroid points))
  (ensure-layer "ROOM-LABELS" 7 "Continuous" 0.20)
  (set-current-layer "ROOM-LABELS")
  
  ;; Create room label text
  (create-text centroid 
               (strcat room-name "\nArea: " (rtos area-val 2 1) " sq ft") 
               18.0 0)
  
  (display-message (strcat "Room '" room-name "' created with area: " (rtos area-val 2 1) " sq ft"))
  area-val
)

;; Function to calculate centroid of polygon
(defun calculate-centroid (points / cx cy n)
  "Calculate centroid of polygon"
  (setq cx 0.0 cy 0.0)
  (setq n (length points))
  
  (foreach pt points
    (setq cx (+ cx (car pt)))
    (setq cy (+ cy (cadr pt)))
  )
  
  (list (/ cx n) (/ cy n))
)

;; Function to create furniture block
(defun create-furniture-block (pos furniture-type rotation scale / block-name)
  "Insert furniture block at specified position"
  (ensure-layer "FURNITURE" 5 "Continuous" 0.20)
  (set-current-layer "FURNITURE")
  
  ;; Define furniture block names
  (cond
    ((= furniture-type "CHAIR") (setq block-name "CHAIR"))
    ((= furniture-type "TABLE") (setq block-name "TABLE"))
    ((= furniture-type "BED") (setq block-name "BED"))
    ((= furniture-type "SOFA") (setq block-name "SOFA"))
    ((= furniture-type "DESK") (setq block-name "DESK"))
    (T (setq block-name "GENERIC"))
  )
  
  ;; Check if block exists, if not create simple representation
  (if (not (tblsearch "BLOCK" block-name))
    (create-simple-furniture-block block-name furniture-type)
  )
  
  ;; Insert furniture block
  (insert-block block-name pos scale rotation)
  
  (display-message (strcat furniture-type " furniture inserted"))
)

;; Function to create simple furniture blocks
(defun create-simple-furniture-block (block-name furniture-type / size pts)
  "Create simple furniture block definitions"
  (cond
    ((= furniture-type "CHAIR")
     (setq size 18)
     (command "._BLOCK" block-name '(0 0) 
              "._RECTANGLE" '(0 0) (list size size) ""))
    
    ((= furniture-type "TABLE")
     (setq size 36)
     (command "._BLOCK" block-name '(0 0) 
              "._CIRCLE" (list (/ size 2) (/ size 2)) (/ size 2) ""))
    
    ((= furniture-type "BED")
     (command "._BLOCK" block-name '(0 0) 
              "._RECTANGLE" '(0 0) '(36 72) ""))
    
    ((= furniture-type "SOFA")
     (command "._BLOCK" block-name '(0 0) 
              "._RECTANGLE" '(0 0) '(24 84) ""))
    
    ((= furniture-type "DESK")
     (command "._BLOCK" block-name '(0 0) 
              "._RECTANGLE" '(0 0) '(24 48) ""))
  )
)

;; Function to create architectural grid
(defun create-architectural-grid (origin x-spacing y-spacing x-count y-count)
  "Create architectural drawing grid with labels"
  (ensure-layer "GRID" 8 "DOT" 0.10)
  (set-current-layer "GRID")
  
  ;; Draw vertical grid lines
  (setq i 0)
  (repeat (1+ x-count)
    (setq x-pos (+ (car origin) (* i x-spacing)))
    (draw-line (list x-pos (cadr origin))
               (list x-pos (+ (cadr origin) (* y-count y-spacing))))
    
    ;; Add grid labels
    (ensure-layer "GRID-LABELS" 7 "Continuous" 0.15)
    (set-current-layer "GRID-LABELS")
    (create-text (list x-pos (- (cadr origin) 12))
                 (chr (+ 65 i))  ;; A, B, C, etc.
                 8.0 0)
    
    (set-current-layer "GRID")
    (setq i (1+ i))
  )
  
  ;; Draw horizontal grid lines
  (setq j 0)
  (repeat (1+ y-count)
    (setq y-pos (+ (cadr origin) (* j y-spacing)))
    (draw-line (list (car origin) y-pos)
               (list (+ (car origin) (* x-count x-spacing)) y-pos))
    
    ;; Add grid labels
    (ensure-layer "GRID-LABELS" 7 "Continuous" 0.15)
    (set-current-layer "GRID-LABELS")
    (create-text (list (- (car origin) 12) y-pos)
                 (itoa (1+ j))  ;; 1, 2, 3, etc.
                 8.0 0)
    
    (set-current-layer "GRID")
    (setq j (1+ j))
  )
  
  (display-message "Architectural grid created with labels")
)

;; Function to create cabinet units
(defun create-cabinet-unit (start-pt end-pt height depth cabinet-type)
  "Create cabinet unit representation"
  (ensure-layer "CABINETS" 6 "Continuous" 0.30)
  (set-current-layer "CABINETS")
  
  ;; Calculate cabinet corners
  (setq cab-angle (angle start-pt end-pt))
  (setq perp-angle (+ cab-angle (/ pi 2)))
  
  (setq corner1 start-pt)
  (setq corner2 end-pt)
  (setq corner3 (polar end-pt perp-angle depth))
  (setq corner4 (polar start-pt perp-angle depth))
  
  ;; Draw cabinet outline
  (draw-polyline (list corner1 corner2 corner3 corner4) T)
  
  ;; Add cabinet details based on type
  (cond
    ((= cabinet-type "BASE")
     ;; Add toe kick line
     (draw-line (polar corner1 perp-angle 3) (polar corner2 perp-angle 3)))
    
    ((= cabinet-type "WALL")
     ;; Add wall mounting indication
     (draw-line corner4 corner3))
    
    ((= cabinet-type "TALL")
     ;; Add center line for tall cabinet
     (setq mid1 (list (/ (+ (car corner1) (car corner4)) 2) (/ (+ (cadr corner1) (cadr corner4)) 2)))
     (setq mid2 (list (/ (+ (car corner2) (car corner3)) 2) (/ (+ (cadr corner2) (cadr corner3)) 2)))
     (draw-line mid1 mid2))
  )
  
  (display-message (strcat cabinet-type " cabinet unit created"))
)

;; Function to check building code compliance
(defun check-building-code-compliance (room-area door-width window-area room-type)
  "Basic building code compliance check"
  (setq violations '())
  
  ;; Check minimum room area
  (cond
    ((and (= room-type "BEDROOM") (< room-area 70))
     (setq violations (append violations '("Bedroom area below 70 sq ft minimum"))))
    ((and (= room-type "BATHROOM") (< room-area 30))
     (setq violations (append violations '("Bathroom area below 30 sq ft minimum"))))
  )
  
  ;; Check door width
  (if (< door-width 32)
    (setq violations (append violations '("Door width below 32 inch minimum (ADA)")))
  )
  
  ;; Check window area (10% of floor area minimum)
  (if (< window-area (* room-area 0.1))
    (setq violations (append violations '("Window area below 10% of floor area")))
  )
  
  ;; Report violations
  (if violations
    (progn
      (princ "\n*** BUILDING CODE VIOLATIONS FOUND ***")
      (foreach violation violations
        (princ (strcat "\n- " violation))
      )
    )
    (princ "\n*** BUILDING CODE COMPLIANCE: PASSED ***")
  )
  
  violations
)

;; Initialize architectural tools
(display-message "Architectural tools loaded successfully")