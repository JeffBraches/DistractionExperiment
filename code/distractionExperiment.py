import pygame #GUI/Multimedia library taken from http://www.pygame.org/
import os
import time
import random
import sys
import string

import eztext #text handling library taken from http://www.pygame.org/project-EzText-920-.html

#pygame imports
from pygame import KEYUP, KEYDOWN, QUIT, K_ESCAPE, K_RETURN, K_x

#Variable Initialization

GUI = None
stack = []
characterLimit = 9
stringLength = 0

distraction = 0
distractionBox = 1
distractionText = 2
distractorType = {
    0: 'No Distractor',
    distractionText: 'Text Distractor',
    distractionBox: 'Colour Box Distractor'
}

screenWidth = 1280
screenHeight = 720
textFont = None

def InitializeProgram():
    global GUI,textEntryArea, experimentData, textFont, textEntryArea
    if len(sys.argv) > 1:
        fname = sys.argv[1] + '.csv'
    else:
        fname = 'DistractionExperimentData'+'.csv'

    GUI = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
    pygame.display.set_caption('Distraction Experiment')
    pygame.init()    
    GUI.fill(color=pygame.Color('#FFFFFF'))
    
    textFont = pygame.font.SysFont('Arial', size=60)

    textEntryArea = eztext.Input(maxlength=9, font=textFont, prompt='Enter the text you saw: ')
    textEntryArea.shifted = True
    textEntryArea.x=0
    textEntryArea.y=650
    ShuffleStack()

    experimentData = open('../data/' + fname, 'w')
    experimentData.write('Displayed, Input, Time to enter, Type of distractor, Match\n')

#randomize distractions
def ShuffleStack():
    global stack
    for i in range(3, characterLimit+1):
        for j in distractorType:
            stack.append( (i,j) )
    random.shuffle(stack)

def DistractorInit(disType, disLength=0):

    side = random.randint(1,2) #1 = right, 2 = left
    if disType is None:
        return
    elif disType == distractionBox:
        distWidth = 300
        distHeight = 100
        top = screenHeight/2 - (distHeight/2)
        right = screenWidth - (distWidth)
        if side == 1:
            GUI.fill(color=pygame.Color('#FF0000'), rect=pygame.Rect(right, top, distWidth, distHeight))
        else:
            GUI.fill(color=pygame.Color('#00FF00'), rect=pygame.Rect(0, top, distWidth, distHeight))
    elif disType == distractionText:
        text = CreateRandomString(disLength)
        mainText = textFont.render(text, True, pygame.Color('#000000'))
        displayTextPosition = mainText.get_rect()
        distractionTextPosition = (0, screenHeight/2 - displayTextPosition.height/2)
        GUI.blit(mainText, distractionTextPosition)

def CreateRandomString(stringLength):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range (0, stringLength))


def RenderText(generatedText=None):

    global distraction
    length = 0

    if generatedText is None:
        length, distraction = stack.pop()
        generatedText = CreateRandomString(length)
        DistractorInit(distraction, length)
    else:
        mainText=generatedText

    mainText = textFont.render(generatedText, True, pygame.Color('#000000'))
    generatedTextPosition = mainText.get_rect(center=(screenWidth/2, screenHeight/2))
    GUI.blit(mainText, generatedTextPosition)
    return generatedText


def WipeGUI():
    GUI.fill(color=pygame.Color('#FFFFFF'))



def SaveData(time, generatedText):
    inputText = textEntryArea.value.upper()
    experimentData.write('%s,%s,%s,%s,%s\n' % (generatedText, inputText, time, distractorType[distraction], inputText==generatedText))
    textEntryArea.value = ''


def Main():

    global stack, distraction
    
    InitializeProgram()

    set_timer = False
    renderTextEntry = False
    experimentBegin = False

    renderTextEvent = pygame.USEREVENT
    guiWipeEvent = pygame.USEREVENT + 1

    globalClock = pygame.time.Clock()
    cycleBeginTime = 0

    generatedText = ''
    RenderText('Press X to begin')

    while True:
        if set_timer:
            if len(stack) == 0: #experiment over
                quit() 
    
    #choose random cycle time between 3 and 5 seconds. Did not implement poisson distribution.
            cycleTime = random.randint(3000, 5000)

    #set flag timers 
            guiWipeFlag = cycleTime + 1000
            pygame.time.set_timer(renderTextEvent, cycleTime)
            pygame.time.set_timer(guiWipeEvent, guiWipeFlag)
            set_timer = False

    #event handling
        eventSet = pygame.event.get()
        for event in eventSet:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quit()
                if event.key == K_RETURN:
                    SaveData(pygame.time.get_ticks() - cycleBeginTime, generatedText)
                    WipeGUI()
                    set_timer = True
                    renderTextEntry = False
                if event.key == K_x and not experimentBegin:
                    set_timer = True
                    experimentBegin = True
                    WipeGUI()

            if event.type == renderTextEvent:
                pygame.time.set_timer(renderTextEvent, 0)
                generatedText = RenderText()

            if event.type == guiWipeEvent:
                pygame.time.set_timer(guiWipeEvent, 0)
                WipeGUI()
                cycleBeginTime = pygame.time.get_ticks()
                renderTextEntry = True
                textEntryArea.value = ''
            if event.type == QUIT:
                quit()

        textEntryArea.update(eventSet)
 
        if renderTextEntry:
            WipeGUI()
            textEntryArea.draw(GUI)

        pygame.display.flip()
        globalClock.tick(120)


def quit():
    experimentData.close()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    Main()
