import cv2
import dlib
import imutils
from scipy.spatial import distance as dist
from imutils import face_utils
from datetime import datetime as dt 

import global_params as gp 
import record as rec 

# some definition: sleepy = doze + yawn 

def avg(list):
	return sum(list)/len(list)

def calc_EAR(eye):
	vert = [dist.euclidean(eye[1], eye[5]),
			dist.euclidean(eye[2], eye[4])] # 0.5*(|p2-p6| + |p3-p5|)
	hori = dist.euclidean(eye[0], eye[3]) # |p4-p1|
	return avg(vert) / hori 

def calc_innerMAR(im): # inner_mouth
	vert = [dist.euclidean(im[1],im[7]), 
			dist.euclidean(im[2],im[6]), 
			dist.euclidean(im[3],im[5])]
	hori = dist.euclidean(im[0],im[4])
	return avg(vert) / hori 
	
def calc_outerMAR(om): # outer_mouth
	vert = [dist.euclidean(om[1], om[11]), 
			dist.euclidean(om[2], om[10]), 
			dist.euclidean(om[3], om[9]), 
			dist.euclidean(om[4], om[8]), 
			dist.euclidean(om[5], om[7])]
	hori = dist.euclidean(om[0],om[6])
	return avg(vert) / hori 

# def check_doze(theEAR):
# 	if theEAR < EAR_THRESH: return True 
# 	else: return False 

# def check_yawn(outerMAR):
# 	if outerMAR > MAR_THRESH: return True
# 	else: return False 

# define parameters 
EAR_THRESH = 0.25
MAR_THRESH = 0.6
FRAME_CHECK = 10

FOURCC = cv2.VideoWriter_fourcc(*'MJPG') # 
FPS = 3
# fourcc = cv2.VideoWriter_fourcc(*'XVID')

def monitor_sleepy(): 
	eyeCount=0
	mouthCount=0
	
	dozeRoute = [] 
	yawnRoute = [] 
	dozeVideo = None
	yawnVideo = None

	detect = dlib.get_frontal_face_detector()
	predict = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")

	(leStart, leEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
	(rStart, reEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
	(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["mouth"]
	(imStart, imEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["inner_mouth"]
	(omStart, omEnd) = (mStart, imStart)

	cap=cv2.VideoCapture(0) # get video 
	print("[INFO] Camera ready")
	gp.cameraReady = True 
	gp.update_allReady()

	while True: 
		if gp.allReady: 
			break
	try: 
		while not gp.arriveDest:
			[ret, frame]=cap.read()
			if not ret: 
				print("Do NOT receive frame. Exiting ...")
				break 
			# frame = imutils.resize(frame, width=480) # make it smaller, easy to compute
			frame = imutils.rotate(frame, 180) # (OPTIONAL) rotation is optional depending on the camera position 
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert frame to gray scale 
			subjects = detect(gray, 0) 

			# add quit message, location and time info on the frame 
			quitStr = "press \"Q\" to quit"
			locStr = "[lat/lon]=[" + str(gp.lat) + "/" + str(gp.lon) + "]"
			timeStr = str(dt.now().strftime('%Y-%m-%d %H:%M:%S'))
			cv2.putText(frame, quitStr, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
			cv2.putText(frame, locStr, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
			cv2.putText(frame, timeStr, (0, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

			for subject in subjects: # multiple subjects for general use 
				shape = predict(gray, subject)
				shape = face_utils.shape_to_np(shape) #converting to NumPy Array

				# get eyes and mouth from shape array 
				leftEye = shape[leStart:leEnd]
				rightEye = shape[rStart:reEnd]
				innerMouth = shape[imStart:imEnd]
				outerMouth = shape[omStart:omEnd]

				# calculate EAR / MAR
				leftEAR = calc_EAR(leftEye)
				rightEAR = calc_EAR(rightEye)
				theEAR = (leftEAR + rightEAR) / 2.0
				outerMAR = calc_outerMAR(outerMouth)
				
				# draw the contours for the eyes and mouth 
				leftEyeHull = cv2.convexHull(leftEye)
				rightEyeHull = cv2.convexHull(rightEye)
				innerMouthHull = cv2.convexHull(innerMouth)
				outerMouthHull = cv2.convexHull(outerMouth)
				cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
				cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
				cv2.drawContours(frame, [innerMouthHull], -1, (255, 0, 0), 1)
				cv2.drawContours(frame, [outerMouthHull], -1, (0, 0, 255), 1)
				
				if (theEAR < EAR_THRESH):
					eyeCount += 1
					print('eyeCount = ', eyeCount)
					if (eyeCount == FRAME_CHECK):
						gp.dozeFlag = True
						dozeSttTime = dt.now() 
						gp.rec_num += 1
						dozeEntryName = "{0}__{1}_doze".format(gp.fname, gp.rec_num)
						dozeRoute.append([dozeSttTime.strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon, gp.road_name])
						if dozeVideo is None: 
							dozeVideo = cv2.VideoWriter(gp.DATA_PATH+dozeEntryName+'.avi', FOURCC, FPS, (int(cap.get(3)), int(cap.get(4))))
					elif (eyeCount > FRAME_CHECK): 
						dozeRoute.append([dt.now().strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon, gp.road_name])
						cv2.putText(frame, "****************ALERT! EYES ****************", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
						dozeVideo.write(frame)
				else: 
					if(eyeCount >= FRAME_CHECK):
						dozeEndTime = dt.now() 
						dozeDurTime = dozeEndTime - dozeSttTime
						dozeSttStr = dozeSttTime.strftime('%Y-%m-%d %H:%M:%S')
						dozeEndStr = dozeEndTime.strftime('%Y-%m-%d %H:%M:%S')
						rec.write_record(dozeEntryName, behavior_type="doze", startTime=dozeSttStr, endTime=dozeEndStr, duration=str(dozeDurTime), route=dozeRoute)
						dozeVideo.release()
						dozeRoute = []
					eyeCount = 0
					gp.dozeFlag = False 

				
				if (outerMAR > MAR_THRESH): 
					mouthCount += 1 
					print('mouthCount = ', mouthCount)
					if (mouthCount == FRAME_CHECK):
						gp.yawnFlag = True
						yawnSttTime = dt.now() 
						gp.rec_num += 1
						yawnEntryName = "{0}__{1}_yawn".format(gp.fname, gp.rec_num)
						yawnRoute.append([yawnSttTime.strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon, gp.road_name])
						if yawnVideo is None: 
							yawnVideo = cv2.VideoWriter(gp.DATA_PATH+yawnEntryName+'.avi', FOURCC, FPS, (int(cap.get(3)), int(cap.get(4))))
					elif (mouthCount > FRAME_CHECK): 
						yawnRoute.append([dt.now().strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon, gp.road_name])
						cv2.putText(frame, "****************ALERT! MOUTH****************", (10,325), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
						yawnVideo.write(frame) 
				else: 
					if(mouthCount > FRAME_CHECK): 			
						yawnEndTime = dt.now() 
						yawnDurTime = yawnEndTime - yawnSttTime
						yawnSttStr = yawnSttTime.strftime('%Y-%m-%d %H:%M:%S')
						yawnEndStr = yawnEndTime.strftime('%Y-%m-%d %H:%M:%S')
						rec.write_record(yawnEntryName, behavior_type="yawn", startTime=yawnSttStr, endTime=yawnEndStr, duration=str(yawnDurTime), route=yawnRoute)
						yawnVideo.release() 
						yawnRoute = []
					mouthCount = 0 
					gp.yawnFlag = False
				
			# cv2.imshow("Frame", frame)
			cv2.imshow("Frame", imutils.resize(frame, width=480))

			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				break
		cap.release() 
		if not (dozeVideo is None): 
			dozeVideo.release() 
		if not (yawnVideo is None): 
			yawnVideo.release() 
		cv2.destroyAllWindows()
	except(KeyboardInterrupt):
		print("[Camera] Exiting ... ")


if __name__=="__main__": 	
	rec.create_record() 
	monitor_sleepy() 

# def detect_sleepy(flag, behavior_type, SttTime, route, count, thresh): 
# 	if (flag != check_behavior(behavior_type, count, thresh)):
# 		if(flag == False): # dangerous behavior on  
# 			SttTime = dt.now() # start time  
# 			route.append([SttTime.strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon])
# 			flag = True 
# 		else: # dangerous behavior off 
# 			EndTime = dt.now() 
# 			DurTime = EndTime - SttTime
# 			SttStr = SttTime.strftime('%Y-%m-%d %H:%M:%S')
# 			EndStr = EndTime.strftime('%Y-%m-%d %H:%M:%S')
# 			DurStr = str(DurTime)
# 			route.append([EndTime.strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon])
# 			rec.write_record(behavior_type=behavior_type, startTime=SttStr, endTime=EndStr, duration=DurStr, route=route)
# 			route = [] 
# 			flag = False 
# 	else: 
# 		if(flag == True): 
# 			route.append([dt.now().strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon])

# def check_behavior(behavior_type, count, thresh):
# 	if (count >= thresh): 
# 		print('[{behavior_type:%s}] count = {count:%d} >= thresh = {thresh:%d}'.format(behavior_type=behavior_type, count=count, thresh=thresh))
# 		return True 
# 	else:
# 		print('[{behavior_type:%s}] count = {count:%d} < thresh = {thresh:%d}'.format(behavior_type=behavior_type, count=count, thresh=thresh))
# 		return False 
	 
