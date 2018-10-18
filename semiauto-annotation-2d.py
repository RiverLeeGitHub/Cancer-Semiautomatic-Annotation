import cv2
import numpy as np

drawing = False
mode = True
enumerated = []
candidates = []
present = None
step = 6


def toshown(img):
    max = img.max()
    min = img.min()
    s = ((255.0/float(max-min))*img-(255.0*min/float(max-min)))
    return s

def min_candidate(candidates):
    min_src=-1
    min_val=float("inf")
    for i in range(len(candidates)):
        try:
            if adc[candidates[i][0]][candidates[i][1]]<min_val:
                min_src = i
                min_val = adc[candidates[i][0]][candidates[i][1]]
        except:
            continue
    return candidates[min_src]

def count_gland_pixel(gland):
    flat = gland.flatten()
    count = 0
    for x in flat:
        if x>0:
            count+=1
    return count



def traversal(i,j,step=6):
    # print "point:",(i,j)
    global enumerated,candidates
    cv2.rectangle(t2w_show, (j-step/2, i-step/2), (j+step/2, i+step/2), (0, 255, 0), -1)
    cv2.rectangle(adc_show, (j-step/2, i-step/2), (j+step/2, i+step/2), (0, 255, 0), -1)
    # cv2.circle(img_show,(j,i),step+1,(0,255,0),-1)

    img_show = np.concatenate([t2w_show,adc_show],axis=1)
    cv2.drawContours(img_show, contours[1], -1, (0, 0, 255), 3)
    cv2.drawContours(adc_show, contours[1], -1, (0, 0, 255), 3)
    cv2.imshow("image", img_show)
    cv2.waitKey(1)
    enumerated.append((i,j))

    try:
        if not (i-step,j) in enumerated and not (i-step,j) in candidates:
            candidates.append((i-step,j))
        if not (i+step,j) in enumerated and not ((i+step,j)) in candidates:
            candidates.append((i+step,j))
        if not (i,j+step) in enumerated and not ((i,j+step)) in candidates:
            candidates.append((i,j+step))
        if not (i,j-step) in enumerated and not ((i,j-step)) in candidates:
            candidates.append((i,j-step))
    except:
        print "Out of boundary"
    next = min_candidate(candidates)## find minimum candidate for extension
    candidates.remove(next)

    return next

def save_annotation(step,path):
    anno = np.zeros(adc.shape,dtype='uint8')
    for x in enumerated:
        anno[x[0]-step/2:x[0]+step/2,x[1]-step/2:x[1]+step/2] = 255
    cv2.imwrite(path,anno)

def EVENT_HANDLER(event,x,y,flags,param):
    global ix,iy,drawing,mode,candidates
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        i,j=y,x
        j = j%len(adc[0])## enable multi-picture drawing

        if gland[i][j]!=0:## the button downs in the gland region
            candidates = []
            next = traversal(i,j,step=step)
            while drawing==True:
                next = traversal(next[0], next[1],step=step)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False


if __name__ == "__main__":

    save_path = "ANNO.png"


    gland = cv2.imread("gland.png")[:,:,0]


    adc = cv2.imread("adc.png")[:,:,0]
    adc_show = np.concatenate([adc[:,:,np.newaxis],adc[:,:,np.newaxis],adc[:,:,np.newaxis]],axis=2)


    ## exclude the part outside the gland
    for i in range(len(adc)):
        for j in range(len(adc[0])):
            if gland[i,j]==0:
                adc[i][j]=255

    ## create the view of image
    t2w = cv2.imread("t2w.png")[:,:,0]
    t2w_show = t2w[:,:,np.newaxis]
    t2w_show = np.concatenate([t2w_show,t2w_show,t2w_show],axis=2)


    ## draw the contours of gland
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3, 3))
    gland = cv2.dilate(gland,kernel)
    contours = cv2.findContours(gland,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(t2w_show,contours[1],-1,(0,0,255),3)
    cv2.drawContours(adc_show,contours[1],-1,(0,0,255),3)

    ## display
    img_show = np.concatenate([t2w_show,adc_show],axis=1)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image',EVENT_HANDLER)

    cv2.imshow("image", img_show)
    while True:

        if cv2.waitKey(2) & 0xFF == ord('q'):
            print "COMMAND q: ",
            print "Quit"
            break
        elif cv2.waitKey(2) & 0xFF == ord('s'):
            print "COMMAND s: ",
            try:
                save_annotation(step, save_path)
                print "Annotation Saved!"
            except:
                print "Saving Error!"
    cv2.destroyAllWindows()
