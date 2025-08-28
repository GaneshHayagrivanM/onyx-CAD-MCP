;; Core AutoLISP functions for AutoCAD MCP Server
;; Basic utility functions used throughout the architectural tools

;; Utility function to create a point list
(defun create-point (x y z)
  "Create a point list from coordinates"
  (list x y z)
)

;; Utility function to get 2D point from 3D
(defun get-2d-point (pt)
  "Extract 2D coordinates from 3D point"
  (list (car pt) (cadr pt))
)

;; Function to calculate distance between two points
(defun point-distance (pt1 pt2)
  "Calculate distance between two points"
  (sqrt (+ (expt (- (car pt2) (car pt1)) 2)
           (expt (- (cadr pt2) (cadr pt1)) 2)
           (expt (- (caddr pt2) (caddr pt1)) 2)))
)

;; Function to calculate angle between two points
(defun point-angle (pt1 pt2)
  "Calculate angle between two points"
  (angle pt1 pt2)
)

;; Function to create a polar point
(defun polar-point (base-pt angle distance)
  "Create a point at polar coordinates from base point"
  (polar base-pt angle distance)
)

;; Function to validate if a point is valid
(defun valid-point-p (pt)
  "Check if point is valid"
  (and (listp pt)
       (>= (length pt) 2)
       (numberp (car pt))
       (numberp (cadr pt)))
)

;; Function to create a layer if it doesn't exist
(defun ensure-layer (layer-name color linetype lineweight)
  "Create layer if it doesn't exist and set properties"
  (if (not (tblsearch "LAYER" layer-name))
    (progn
      (command "._LAYER" "N" layer-name "C" color layer-name 
               "LT" linetype layer-name "LW" lineweight layer-name "")
      (princ (strcat "\nLayer " layer-name " created."))
    )
    (princ (strcat "\nLayer " layer-name " already exists."))
  )
)

;; Function to set current layer
(defun set-current-layer (layer-name)
  "Set the current active layer"
  (setvar "CLAYER" layer-name)
)

;; Function to draw a rectangle
(defun draw-rectangle (pt1 pt2)
  "Draw a rectangle from two diagonal points"
  (command "._RECTANGLE" pt1 pt2)
)

;; Function to draw a line
(defun draw-line (pt1 pt2)
  "Draw a line between two points"
  (command "._LINE" pt1 pt2 "")
)

;; Function to draw a polyline from point list
(defun draw-polyline (points closed)
  "Draw a polyline from list of points"
  (command "._PLINE")
  (foreach pt points
    (command pt)
  )
  (if closed
    (command "C")
    (command "")
  )
)

;; Function to draw a circle
(defun draw-circle (center radius)
  "Draw a circle"
  (command "._CIRCLE" center radius)
)

;; Function to draw an arc
(defun draw-arc (center start-angle end-angle radius)
  "Draw an arc"
  (command "._ARC" "C" center (polar center start-angle radius) 
           (polar center end-angle radius))
)

;; Function to create text
(defun create-text (position text-string height rotation)
  "Create text entity"
  (command "._TEXT" position height rotation text-string)
)

;; Function to create multiline text
(defun create-mtext (position width text-string height)
  "Create multiline text"
  (command "._MTEXT" position "W" width text-string "")
)

;; Function to create a linear dimension
(defun create-linear-dim (pt1 pt2 dim-line-pt)
  "Create linear dimension"
  (command "._DIMLINEAR" pt1 pt2 dim-line-pt)
)

;; Function to create an angular dimension
(defun create-angular-dim (center-pt pt1 pt2 arc-pt)
  "Create angular dimension"
  (command "._DIMANGULAR" center-pt pt1 pt2 arc-pt)
)

;; Function to insert a block
(defun insert-block (block-name position scale rotation)
  "Insert a block"
  (command "._INSERT" block-name position scale scale rotation)
)

;; Function to zoom to extents
(defun zoom-extents ()
  "Zoom to drawing extents"
  (command "._ZOOM" "_E")
)

;; Function to regenerate drawing
(defun regen-drawing ()
  "Regenerate the drawing"
  (command "._REGEN")
)

;; Function to save drawing
(defun save-drawing (filepath)
  "Save drawing to specified path"
  (command "._SAVEAS" "2018" filepath)
)

;; Function to calculate polygon area using shoelace formula
(defun polygon-area (points)
  "Calculate area of polygon using shoelace formula"
  (setq area 0.0)
  (setq n (length points))
  (setq i 0)
  (repeat n
    (setq j (if (= i (1- n)) 0 (1+ i)))
    (setq pt1 (nth i points))
    (setq pt2 (nth j points))
    (setq area (+ area (- (* (car pt1) (cadr pt2)) (* (car pt2) (cadr pt1)))))
    (setq i (1+ i))
  )
  (abs (/ area 2.0))
)

;; Function to get user input with validation
(defun get-point-input (prompt)
  "Get point input from user with validation"
  (setq pt (getpoint prompt))
  (while (not (valid-point-p pt))
    (princ "\nInvalid point. Please try again.")
    (setq pt (getpoint prompt))
  )
  pt
)

;; Function to get positive number input
(defun get-positive-real (prompt)
  "Get positive real number from user"
  (setq val (getreal prompt))
  (while (or (not (numberp val)) (<= val 0))
    (princ "\nValue must be a positive number. Please try again.")
    (setq val (getreal prompt))
  )
  val
)

;; Function to get string input
(defun get-string-input (prompt)
  "Get string input from user"
  (setq str (getstring prompt))
  (while (or (not str) (= str ""))
    (princ "\nString cannot be empty. Please try again.")
    (setq str (getstring prompt))
  )
  str
)

;; Function to display message with formatting
(defun display-message (msg)
  "Display formatted message"
  (princ (strcat "\n*** " msg " ***\n"))
)

;; Function to log error
(defun log-error (func-name error-msg)
  "Log error message"
  (princ (strcat "\nERROR in " func-name ": " error-msg))
)

;; Initialize core functions
(display-message "Core AutoLISP functions loaded successfully")