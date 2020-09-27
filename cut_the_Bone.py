# coding=utf-8
import cv2
from ct_exception import CT_Exception

margin = 15


def bone_cutting_black_v2(img):
    '''
        specifically for the black background images
    '''
    img = img[95:, :1950]
    img_processed = grayscale_threshold(img)
    borders_x = [];
    count = 0
    for i in range(img_processed.shape[1]):
        if img_processed[110][i] > 200:
            count += 1
        elif count != 0 and img_processed[110][i] < 100:
            if count > 400:
                borders_x.append(i - count)
                borders_x.append(i)
            count = 0
    borders_y = 0;
    borders_height = 0
    find_y = find_height = False
    temp_x = borders_x[1] - borders_x[0]
    for i in range(img_processed.shape[0]):
        if find_y and find_height:
            break
        if img_processed[i][temp_x] > 200:
            find_y = True
            borders_y = i

        if img_processed[img_processed.shape[0] - i - 1][temp_x] > 200:
            find_height = True
            borders_height = img_processed.shape[0] - i - 1
    y = borders_y - margin;
    height = borders_height + margin;
    x = borders_x[0];
    width = borders_x[1]
    if y < 0:
        y = 0
    if x < 0:
        x = 0
    left_one_cut_image = img[y:height, x:width]
    x = borders_x[2];
    width = borders_x[3]
    if x < 0:
        x = 0
    left_two_cut_image = img[y:height, x:width]

    borders = find_borders(vertical_projection(grayscale_threshold(left_one_cut_image)))
    borders = check_borders(borders)
    y = borders[0] - margin;
    height = borders[1] + margin
    if y < 0:
        y = 0
    left_one_cut_image = left_one_cut_image[y:height, :]

    borders = find_borders(vertical_projection(grayscale_threshold(left_two_cut_image)))
    borders = check_borders(borders)
    y = borders[0] - margin;
    height = borders[1] + margin
    if y < 0:
        y = 0
    left_two_cut_image = left_two_cut_image[y:height, :]

    return [left_one_cut_image, left_two_cut_image]


def bone_cutting_white(img):
    '''
        Specifically for the white background images
    '''

    img_processed = grayscale_threshold(img)
    horizontal_borders = find_borders(horizontal_projection(img_processed))
    vertical_borders = find_borders(vertical_projection(img_processed))
    y = vertical_borders[0] - margin;
    height = vertical_borders[1] + margin;
    x = horizontal_borders[0] - margin;
    width = horizontal_borders[1] + margin
    if y < 0:
        y = 0
    if x < 0:
        x = 0
    left_one_cut_image = img[y:height, x:width]
    x = horizontal_borders[2] - margin;
    width = horizontal_borders[3] + margin
    if x < 0:
        x = 0
    left_two_cut_image = img[y:height, x:width]
    return [left_one_cut_image, left_two_cut_image]


def bone_cutting_black_cth(img):
    img = img[45:, 26:]
    grayed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    isWhite = False;
    startPoint = 0
    for i in range(0, grayed_img.shape[0]):
        if isWhite == False and grayed_img[i][0] > 100:  # if the point is white
            startPoint = i
            isWhite = True
        elif isWhite == True and grayed_img[i][0] < 100:  # if the point is black
            img = img[startPoint:i, :]
            break
    grayed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    pointList = [0]
    isBlack = False
    index = 0
    while index < grayed_img.shape[1]:
        if isBlack == False and grayed_img[0][index] < 100:  # the point is black
            pointList.append(index)
            isBlack = True
        elif isBlack == True and grayed_img[0][index] > 100:  # the point is white
            pointList.append(index)
            isBlack = False
        index += 1

    # Cut bone
    cutting_imgs = []
    for i in range(0, len(pointList), 2):
        tempImg = img[:, pointList[i]:pointList[i + 1]]
        cutting_imgs.append(tempImg)
    return cutting_imgs


def bone_cutting_gray(img):
    grayed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, grayed_img = cv2.threshold(grayed_img, 240, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))  # define kernel
    grayed_img = cv2.erode(grayed_img, kernel)

    grayed_leftImg, grayed_rightImg, leftImg, rightImg = seperateLeftRightPartsAndCutBlackMargin(grayed_img, img)

    _, _, leftLeftImg, LeftRightImg = seperateLeftRightPartsAndCutBlackMargin(grayed_leftImg, leftImg)
    cutting_imgs = []
    cutting_imgs.append(leftLeftImg)
    cutting_imgs.append(LeftRightImg)
    _, _, rightLeftImg, rightRightImg = seperateLeftRightPartsAndCutBlackMargin(grayed_rightImg, rightImg)
    cutting_imgs.append(rightLeftImg)
    cutting_imgs.append(rightRightImg)
    return cutting_imgs


def bone_cutting(img):
    '''
        The main function to cut the bone from the origin image
    '''

    left_top_img = grayscale_threshold(img[:, :25])
    blacks = count_blacks(left_top_img)
    if blacks >= 25 * img.shape[0] / 2:
        print("black")
        right_top_img = cut_right_top_corner(img, 50, colorBase="blue")
        count0_80 = 0;
        count80_150 = 0;
        count150_255 = 0

        for i in range(right_top_img.shape[0]):
            for j in range(right_top_img.shape[1]):
                if right_top_img[i][j] < 80:
                    count0_80 += 1
                elif 80 <= right_top_img[i][j] and right_top_img[i][j] <= 150:
                    count80_150 += 1
                elif 150 < right_top_img[i][j]:
                    count150_255 += 1

        if count0_80 > count80_150 and count0_80 > count150_255:  # 耕莘醫院的黑底圖
            cutting_temp = bone_cutting_black_cth(img)
            cutting_imgs = [cutting_temp[2], cutting_temp[3]]
        elif count80_150 > count0_80 and count80_150 > count150_255:  # 秀傳醫院的黑底圖
            cutting_imgs = bone_cutting_black_v2(img)
            cutting_imgs = check_bottom_characters(cutting_imgs)
        elif count150_255 > count0_80 and count150_255 > count80_150:  # 耕莘醫院的灰底圖
            grayed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            left_top_img = grayed_img[:60, :180]
            _, left_top_img = cv2.threshold(left_top_img, 200, 255, cv2.THRESH_BINARY)
            blacks = count_blacks(left_top_img)
            if blacks >= 60 * 180 / 2:  # 耕莘醫院灰底圖2 e.g. : Picture6.png
                img = img[110:, :]
                cutting_temp = bone_cutting_gray(img)
                cutting_imgs = [cutting_temp[1], cutting_temp[3]]
            else:  # 耕莘醫院灰底圖1 e.g. : Picture5.png
                img = img[70:, :]
                cutting_temp = bone_cutting_gray(img)
                cutting_imgs = [cutting_temp[1], cutting_temp[3]]

    else:
        print("white")
        right_top_img = cut_right_top_corner(img, 40)
        blacks = count_blacks(right_top_img)
        if blacks >= 40 * 40 / 2:
            right_40_img = grayscale_threshold(img[:, img.shape[1] - 40:])
            blacks = count_blacks(right_40_img)
            if blacks >= right_40_img.shape[0] * 40 / 2:  # 耕莘醫院灰底圖3 e.g.: Picture7.png
                grayedImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresholdedImg = cv2.threshold(grayedImg, 200, 255, cv2.THRESH_BINARY)
                projections = vertical_projection(thresholdedImg)
                for i in range(len(projections)):
                    if projections[i] == thresholdedImg.shape[1]:
                        img = img[i:, :]
                        break
                projections = horizontal_projection(thresholdedImg)
                for i in range(len(projections)):
                    if projections[i] == thresholdedImg.shape[0]:
                        img = img[:, :i]
                        break
                cutting_temp = bone_cutting_gray(img)
                cutting_imgs = [cutting_temp[1], cutting_temp[3]]
            else:  # 耕莘醫院的白底圖 e.g: Picture2.png
                img = img[45:, int(img.shape[1] / 2):]
                print("A")
                cv2.imwrite("test.jpg", img)
                cutting_imgs = bone_cutting_white(img)
        else:  # 秀傳醫院的白底圖
            img = img[120:img.shape[0] - 50, 0:]
            cutting_imgs = bone_cutting_white(img)
    # check the imgs fits what we need (need the whole body, not just legs or arms)
    Is_what_we_need = check_is_what_we_need(cutting_imgs, img)
    print(Is_what_we_need)
    if Is_what_we_need:
        return cutting_imgs
    else:
        raise CT_Exception("Not_what_we_need:", cutting_imgs)

def check_is_what_we_need(cutting_imgs, img):
    for bone_img in cutting_imgs:
        if bone_img.shape[0] < int(img.shape[0] * 0.5):
            return False
        else:
            return True


def cut_right_top_corner(img, width, colorBase="gray"):
    '''
        Cut width * width's square from the right top of the image.
    '''
    if colorBase == "gray":
        right_top_img = grayscale_threshold(img[:width, img.shape[1] - width:])
        return right_top_img
    elif colorBase == "blue":
        img = img[:width, img.shape[1] - width:]
        b, _, _ = cv2.split(img)
        return b


def get_height_with_ConnectedComponent(bone_img):
    source = grayscale_threshold(bone_img)
    m = source.shape[0]
    n = source.shape[1]
    # the 2 Dimension set list
    pointToSet = []
    for i in range(0, m):
        tmp = []
        for j in range(0, n):
            tmp.append(set())
        pointToSet.append(tmp)

    blockSet = []
    for i in range(0, m):
        for j in range(0, n):
            if (source[i][j] < 240):
                if (i - 1 >= 0 and len(pointToSet[i - 1][j]) > 0):
                    pointToSet[i - 1][j].add(i * n + j)
                    pointToSet[i][j] = pointToSet[i - 1][j]

                    if j - 1 >= 0 and len(pointToSet[i][j - 1]) > 0 and pointToSet[i - 1][j] != pointToSet[i][j - 1]:
                        s = pointToSet[i][j - 1]
                        for x in s:
                            pointToSet[int(x / n)][int(x % n)] = pointToSet[i - 1][j]
                            pointToSet[i - 1][j].add(x)
                        s.clear()
                        blockSet.remove(s)

                elif j - 1 >= 0 and len(pointToSet[i][j - 1]) > 0:
                    pointToSet[i][j - 1].add(i * n + j)
                    pointToSet[i][j] = pointToSet[i][j - 1]
                else:
                    hs = set()
                    hs.add(i * n + j)
                    pointToSet[i][j] = hs
                    blockSet.append(hs)
    # --------------------------------------------
    y1 = source.shape[0]
    y2 = 0
    img_heights = []
    for hs in blockSet:
        if len(hs) > 5000:
            for k in hs:
                tmp_y = int(k / n)
                y1 = min(y1, tmp_y)
                y2 = max(y2, tmp_y)
            img_heights.append(y2 - y1)
    return img_heights


def count_blacks(img):
    '''
        Count how many black pixels to differentiate the black or white background images
    '''
    blacks = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i][j] < 100:
                blacks += 1
    return blacks


def grayscale_threshold(img):
    '''
        Do grayscale, erode and threshold to the input image
    '''
    _, img = cv2.threshold(
        cv2.erode(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))), 250, 255,
        cv2.THRESH_BINARY)
    return img


def horizontal_projection(img):
    '''
        count the black numbers in horizontal direction
    '''
    black_counters = []
    for i in range(img.shape[1]):
        black_counters.append(0)
        for j in range(img.shape[0]):
            if img[j][i] < 100:
                black_counters[i] += 1
    return black_counters


def vertical_projection(img):
    '''
        count the black numbers in vertical direction
    '''
    black_counters = []
    for i in range(img.shape[0]):
        black_counters.append(0)
        for j in range(img.shape[1]):
            if img[i][j] < 100:
                black_counters[i] += 1
    return black_counters


def find_borders(black_counters):
    '''
        find the white & black border with the black_counters
        return : list (contains the borders' position)
    '''
    find = False
    borders = []
    for i in range(len(black_counters)):
        if (not find and black_counters[i] >= 100):
            find = True
            borders.append(i)
        elif (find and black_counters[i] < 100):
            find = False
            borders.append(i)
    if find:
        borders.append(len(black_counters) - 1)
    tmp = [];
    x = 0;
    y = 0
    for border in borders:
        if len(tmp) == 0 or len(tmp) == 1:
            tmp.append(border)
        else:
            if x == 0:
                x = border
            elif y == 0:
                y = border
            if x != 0 and y != 0:
                if x - tmp[len(tmp) - 1] < 50:
                    tmp[len(tmp) - 1] = y
                else:
                    tmp.append(x)
                    tmp.append(y)
                x = 0;
                y = 0
    return tmp


def check_borders(borders):
    tmp = []
    for i in range(0, len(borders), 2):
        border1 = borders[i]
        border2 = borders[i + 1]
        if border2 - border1 >= 800:
            tmp.append(border1)
            tmp.append(border2)
    return tmp


def check_bottom_characters(img_list):
    '''
        Check if there are any characters at the bottom of the image.
    '''
    tmp = []
    for img in img_list:
        cut_position_y = int(img.shape[0] * 0.8)
        cut_img = cv2.cvtColor(img[cut_position_y:, :], cv2.COLOR_BGR2GRAY)
        black_counters = vertical_projection(cut_img)
        find = False
        for i in range(len(black_counters)):
            if black_counters[i] > 50:
                find = True
                cut_position_y += i
                break
        if find:
            tmp.append(img[:cut_position_y - margin, :])
        else:
            tmp.append(img)
    return tmp


# 2020/02/05:耕莘醫院用
def findLeftTopPoint(img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i][j] > 100 and img[i + 1][j] > 100 and img[i][j + 1] > 100 and img[i + 1][
                j + 1] > 100:  # if the point is white
                for k in range(i):  # loop upward until the upper pixel is black.
                    if i - k - 1 < 0:
                        return 0, j
                    if img[i - k - 1][j] < 100:  # if the point is black
                        return i - k, j
                return 0, j


def findLeftBottomPoint(img):
    for i in range(img.shape[0] - 1, 0, -1):
        for j in range(img.shape[1]):
            if img[i][j] > 100 and img[i - 1][j] > 100 and img[i][j + 1] and img[i - 1][
                j + 1] > 100:  # if the point is white
                for k in range(img.shape[0] - i):  # loop downward until the lower pixel is black.
                    if i + k + 1 >= img.shape[0]:
                        return img.shape[0], j
                    if img[i + k + 1][j] < 100:  # if the point is black
                        return i + k, j
                return img.shape[0], j


def findRightTopPoint(img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1] - 1, 0, -1):
            if img[i][j] > 100 and img[i + 1][j] > 100 and img[i][j - 1] > 100 and img[i + 1][
                j - 1] > 100:  # if the point is white
                for k in range(i):  # loop upward until the upper pixel is black.
                    if i - k - 1 < 0:
                        return 0, j
                    if img[i - k - 1][j] < 100:  # if the point is black
                        return i - k, j
                return 0, j


def findRightBottomPoint(img):
    for i in range(img.shape[0] - 1, 0, -1):
        for j in range(img.shape[1] - 1, 0, -1):
            if img[i][j] > 100 and img[i - 1][j] > 100 and img[i][j - 1] > 100 and img[i - 1][
                j - 1] > 100:  # if the point is white
                for k in range(img.shape[0] - i):  # loop downward until the lower pixel is black.
                    if i + k + 1 >= img.shape[0]:
                        return img.shape[0], j
                    if img[i + k + 1][j] < 100:  # if the point is black
                        return i + k, j
                return img.shape[0], j


def cutBlackMarginsAround(grayed_Img, Img):
    leftTopY, leftTopX = findLeftTopPoint(grayed_Img)
    leftBottomY, leftBottomX = findLeftBottomPoint(grayed_Img)
    rightTopY, rightTopX = findRightTopPoint(grayed_Img)
    rightBottomY, rightBottomX = findRightBottomPoint(grayed_Img)

    leftTopY = max(leftTopY, rightTopY)
    leftTopX = max(leftTopX, leftBottomX)
    rightBottomY = min(rightBottomY, leftBottomY)
    rightBottomX = min(rightBottomX, rightTopX)
    # print(leftTopY,",",leftTopX)
    # print(rightBottomY,",",rightBottomX)
    return grayed_Img[leftTopY:rightBottomY, leftTopX:rightBottomX], Img[leftTopY:rightBottomY, leftTopX:rightBottomX]


def seperateLeftRightPartsAndCutBlackMargin(grayedImg, img):
    grayedLeftImg = grayedImg[:, :int(grayedImg.shape[1] / 2)]
    grayedRightImg = grayedImg[:, int(grayedImg.shape[1] / 2):]

    leftImg = img[:, :int(img.shape[1] / 2)]
    rightImg = img[:, int(img.shape[1] / 2):]

    grayedLeftImg, leftImg = cutBlackMarginsAround(grayedLeftImg, leftImg)
    grayedRightImg, rightImg = cutBlackMarginsAround(grayedRightImg, rightImg)
    return grayedLeftImg, grayedRightImg, leftImg, rightImg