;; Utility functions for AutoCAD MCP Server
;; Additional helper functions and advanced features

;; Load core functions
(load "core_functions.lsp")

;; Function to generate room schedule
(defun generate-room-schedule (room-list / schedule-text total-area)
  "Generate room schedule table"
  (setq schedule-text "ROOM SCHEDULE\n")
  (setq schedule-text (strcat schedule-text "=============\n"))
  (setq schedule-text (strcat schedule-text "Room Name       Area (sq ft)\n"))
  (setq schedule-text (strcat schedule-text "--------------------------------\n"))
  (setq total-area 0.0)
  
  (foreach room room-list
    (setq room-name (car room))
    (setq room-area (cadr room))
    (setq total-area (+ total-area room-area))
    (setq schedule-text (strcat schedule-text 
                               room-name 
                               (substr "                " 1 (- 16 (strlen room-name)))
                               (rtos room-area 2 1) 
                               "\n"))
  )
  
  (setq schedule-text (strcat schedule-text "--------------------------------\n"))
  (setq schedule-text (strcat schedule-text "TOTAL           " (rtos total-area 2 1) "\n"))
  
  ;; Create schedule as multiline text
  (ensure-layer "SCHEDULES" 7 "Continuous" 0.20)
  (set-current-layer "SCHEDULES")
  (create-mtext '(0 0) 200 schedule-text 8.0)
  
  (display-message "Room schedule generated")
  schedule-text
)

;; Function to export drawing to various formats
(defun export-drawing (format-type filepath / cmd-string)
  "Export drawing to specified format"
  (cond
    ((= format-type "PDF")
     (command "._PLOT" "Y" "" "DWG To PDF.pc3" "ARCH D (36.00 x 24.00 Inches)" "I" "L" "N" "E" "F" "C" "Y" filepath "N" "Y"))
    
    ((= format-type "DXF")
     (command "._SAVEAS" "DXF" filepath))
    
    ((= format-type "DWG")
     (command "._SAVEAS" "2018" filepath))
    
    ((= format-type "WMF")
     (command "._WMFOUT" filepath ""))
    
    (T 
     (princ "\nUnsupported export format"))
  )
  
  (display-message (strcat "Drawing exported to " format-type " format"))
)

;; Function to create parametric components
(defun create-parametric-component (base-pt component-type parameters / comp-width comp-height comp-depth)
  "Create parametric architectural components"
  (setq comp-width (cdr (assoc "width" parameters)))
  (setq comp-height (cdr (assoc "height" parameters)))
  (setq comp-depth (cdr (assoc "depth" parameters)))
  
  (cond
    ((= component-type "COLUMN")
     (create-column base-pt comp-width comp-height))
    
    ((= component-type "BEAM")
     (create-beam base-pt comp-width comp-height comp-depth))
    
    ((= component-type "STAIR")
     (create-stair base-pt parameters))
    
    ((= component-type "RAMP")
     (create-ramp base-pt parameters))
    
    (T
     (princ "\nUnsupported component type"))
  )
)

;; Function to create structural column
(defun create-column (base-pt width height / corner-pts)
  "Create structural column"
  (ensure-layer "STRUCTURE" 1 "Continuous" 0.50)
  (set-current-layer "STRUCTURE")
  
  ;; Create column base
  (setq corner-pts (list base-pt
                         (list (+ (car base-pt) width) (cadr base-pt))
                         (list (+ (car base-pt) width) (+ (cadr base-pt) width))
                         (list (car base-pt) (+ (cadr base-pt) width))))
  
  (draw-polyline corner-pts T)
  
  ;; Add column centerlines
  (ensure-layer "STRUCTURE-CENTER" 8 "CENTER" 0.25)
  (set-current-layer "STRUCTURE-CENTER")
  
  (setq center-pt (list (+ (car base-pt) (/ width 2)) (+ (cadr base-pt) (/ width 2))))
  (draw-line (list (car center-pt) (- (cadr center-pt) (/ width 2)))
             (list (car center-pt) (+ (cadr center-pt) (/ width 2))))
  (draw-line (list (- (car center-pt) (/ width 2)) (cadr center-pt))
             (list (+ (car center-pt) (/ width 2)) (cadr center-pt)))
  
  (display-message "Structural column created")
)

;; Function to create structural beam
(defun create-beam (start-pt width height depth / end-pt beam-pts)
  "Create structural beam"
  (ensure-layer "STRUCTURE" 1 "Continuous" 0.50)
  (set-current-layer "STRUCTURE")
  
  (setq end-pt (list (+ (car start-pt) width) (cadr start-pt)))
  
  ;; Draw beam outline
  (draw-rectangle start-pt (list (+ (car start-pt) width) (+ (cadr start-pt) depth)))
  
  ;; Add beam centerline
  (ensure-layer "STRUCTURE-CENTER" 8 "CENTER" 0.25)
  (set-current-layer "STRUCTURE-CENTER")
  (draw-line (list (car start-pt) (+ (cadr start-pt) (/ depth 2)))
             (list (+ (car start-pt) width) (+ (cadr start-pt) (/ depth 2))))
  
  (display-message "Structural beam created")
)

;; Function to create stairs
(defun create-stair (base-pt parameters / width run rise num-steps step-width total-run step-pts i)
  "Create stair representation"
  (setq width (cdr (assoc "width" parameters)))
  (setq run (cdr (assoc "run" parameters)))
  (setq rise (cdr (assoc "rise" parameters)))
  (setq num-steps (cdr (assoc "steps" parameters)))
  
  (ensure-layer "STAIRS" 6 "Continuous" 0.30)
  (set-current-layer "STAIRS")
  
  (setq step-width (/ run num-steps))
  (setq total-run (* step-width num-steps))
  
  ;; Draw stair outline
  (draw-rectangle base-pt (list (+ (car base-pt) total-run) (+ (cadr base-pt) width)))
  
  ;; Draw individual steps
  (setq i 0)
  (repeat num-steps
    (setq step-x (+ (car base-pt) (* i step-width)))
    (draw-line (list step-x (cadr base-pt))
               (list step-x (+ (cadr base-pt) width)))
    (setq i (1+ i))
  )
  
  ;; Add direction arrow
  (ensure-layer "STAIR-NOTES" 7 "Continuous" 0.20)
  (set-current-layer "STAIR-NOTES")
  (setq arrow-start (list (+ (car base-pt) 12) (+ (cadr base-pt) (/ width 2))))
  (setq arrow-end (list (+ (car base-pt) total-run -12) (+ (cadr base-pt) (/ width 2))))
  (draw-line arrow-start arrow-end)
  
  ;; Add "UP" text
  (create-text (list (+ (car base-pt) (/ total-run 2)) (+ (cadr base-pt) (/ width 2)))
               "UP" 8.0 0)
  
  (display-message "Stairs created")
)

;; Function to load drawing template
(defun load-drawing-template (template-name / template-file)
  "Load predefined drawing template"
  (cond
    ((= template-name "RESIDENTIAL")
     (setup-residential-template))
    
    ((= template-name "COMMERCIAL")
     (setup-commercial-template))
    
    ((= template-name "SITE_PLAN")
     (setup-site-plan-template))
    
    (T
     (princ "\nTemplate not found, using default"))
  )
)

;; Function to setup residential template
(defun setup-residential-template ()
  "Setup layers and settings for residential drawings"
  ;; Create standard residential layers
  (ensure-layer "WALLS" 1 "Continuous" 0.35)
  (ensure-layer "DOORS" 3 "Continuous" 0.25)
  (ensure-layer "WINDOWS" 4 "Continuous" 0.25)
  (ensure-layer "ROOMS" 2 "PHANTOM" 0.15)
  (ensure-layer "FURNITURE" 5 "Continuous" 0.20)
  (ensure-layer "DIMENSIONS" 6 "Continuous" 0.15)
  (ensure-layer "TEXT" 7 "Continuous" 0.15)
  (ensure-layer "GRID" 8 "DOT" 0.10)
  
  ;; Set drawing units and precision
  (setvar "LUNITS" 4)    ; Architectural units
  (setvar "LUPREC" 4)    ; 1/16" precision
  (setvar "DIMSCALE" 48) ; 1/4" = 1'-0" scale
  
  (display-message "Residential template loaded")
)

;; Function to setup commercial template  
(defun setup-commercial-template ()
  "Setup layers and settings for commercial drawings"
  ;; Create standard commercial layers
  (ensure-layer "WALLS" 1 "Continuous" 0.50)
  (ensure-layer "DOORS" 3 "Continuous" 0.30)
  (ensure-layer "WINDOWS" 4 "Continuous" 0.30)
  (ensure-layer "STRUCTURE" 1 "Continuous" 0.70)
  (ensure-layer "MECHANICAL" 13 "HIDDEN" 0.25)
  (ensure-layer "ELECTRICAL" 14 "PHANTOM" 0.25)
  (ensure-layer "PLUMBING" 12 "DOT" 0.25)
  (ensure-layer "FIRE-SAFETY" 1 "Continuous" 0.35)
  
  ;; Set commercial drawing standards
  (setvar "LUNITS" 4)     ; Architectural units
  (setvar "LUPREC" 4)     ; 1/16" precision
  (setvar "DIMSCALE" 96)  ; 1/8" = 1'-0" scale
  
  (display-message "Commercial template loaded")
)

;; Function to generate 3D model (basic extrusion)
(defun generate-3d-model-from-plan (extrude-height)
  "Generate basic 3D model by extruding 2D elements"
  (ensure-layer "3D-MODEL" 7 "Continuous" 0.25)
  (set-current-layer "3D-MODEL")
  
  ;; Select all closed polylines (rooms, walls)
  (setq selection (ssget "X" '((0 . "LWPOLYLINE"))))
  
  (if selection
    (progn
      (setq i 0)
      (repeat (sslength selection)
        (setq ent (ssname selection i))
        (command "._EXTRUDE" ent "" extrude-height)
        (setq i (1+ i))
      )
      (display-message "3D model generated")
    )
    (princ "\nNo polylines found to extrude")
  )
)

;; Function to create section view
(defun create-section-view (start-pt end-pt depth view-name)
  "Create section view indication"
  (ensure-layer "SECTIONS" 1 "PHANTOM2" 0.40)
  (set-current-layer "SECTIONS")
  
  ;; Draw section line
  (draw-line start-pt end-pt)
  
  ;; Add section markers
  (setq marker-size 6)
  (draw-circle start-pt marker-size)
  (draw-circle end-pt marker-size)
  
  ;; Add section labels
  (ensure-layer "SECTION-LABELS" 7 "Continuous" 0.20)
  (set-current-layer "SECTION-LABELS")
  (create-text (list (car start-pt) (- (cadr start-pt) 12)) view-name 8.0 0)
  (create-text (list (car end-pt) (- (cadr end-pt) 12)) view-name 8.0 0)
  
  (display-message (strcat "Section " view-name " created"))
)

;; Function to create elevation reference
(defun create-elevation-reference (base-line view-direction elevation-name)
  "Create elevation reference markers"
  (ensure-layer "ELEVATIONS" 1 "CONTINUOUS" 0.30)
  (set-current-layer "ELEVATIONS")
  
  (setq start-pt (car base-line))
  (setq end-pt (cadr base-line))
  
  ;; Draw elevation reference line
  (draw-line start-pt end-pt)
  
  ;; Add directional arrow
  (setq mid-pt (list (/ (+ (car start-pt) (car end-pt)) 2) 
                     (/ (+ (cadr start-pt) (cadr end-pt)) 2)))
  (setq arrow-angle (cond
                      ((= view-direction "NORTH") (/ pi 2))
                      ((= view-direction "SOUTH") (* 3 (/ pi 2)))
                      ((= view-direction "EAST") 0)
                      ((= view-direction "WEST") pi)
                      (T 0)))
  
  (setq arrow-end (polar mid-pt arrow-angle 12))
  (draw-line mid-pt arrow-end)
  
  ;; Add elevation label
  (ensure-layer "ELEVATION-LABELS" 7 "Continuous" 0.20)
  (set-current-layer "ELEVATION-LABELS")
  (create-text arrow-end elevation-name 8.0 0)
  
  (display-message (strcat "Elevation " elevation-name " reference created"))
)

;; Initialize utility functions
(display-message "Utility functions loaded successfully")