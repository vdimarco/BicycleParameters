import os
import re
import pickle
from math import pi
import numpy as np
from numpy.linalg import inv
from scipy.optimize import leastsq
from scipy.io import loadmat
from uncertainties import ufloat, unumpy

class Bicycle(object):
    '''An object for a bicycle. A bicycle has parameters. That's about it for
    now.

    '''

    def __new__(cls, shortname, forceRawCalc=False):
        '''Returns a NoneType object if there is no directory'''
        # is there a data directory for this bicycle? if not, tell the user to
        # put some data in the folder so we have something to work with!
        try:
            if os.path.isdir(os.path.join('bicycles', shortname)) == True:
                print "We have foundeth a directory named: bicycles/" + shortname
                return super(Bicycle, cls).__new__(cls)
            else:
                raise ValueError
        except:
            a = "Are you nuts?! Make a directory with basic data for your "
            b = "bicycle in bicycles/shortname, where 'shortname' is the "
            c = "capitalized one word name of your bicycle. Then I can "
            d = "actually created a bicycle object."
            print a + b + c + d
            return None

    def __init__(self, shortname, forceRawCalc=False):
        '''
        Sets the parameters if there any that are already saved.

        Arguments
        ---------
        shortname : string
            shortname of your bicicleta, one word, first letter is capped and
            should match a directory under bicycles/

        forceRawCalc : boolean
            Force a recalculation of the parameters from the raw data, else it
            will only do this calculation if there are no parameter files.

        '''

        self.shortname = shortname
        self.directory = os.path.join('bicycles', shortname)
        self.parameters = {}

        # if you want to force a recalculation and there is a RawData directory
        if forceRawCalc and 'RawData' in os.listdir(self.directory):
            self.parameters['Benchmark'] = self.calculate_from_measured()
        elif not forceRawCalc and 'Parameters' not in os.listdir(self.directory):
            self.parameters['Benchmark'] = self.calculate_from_measured()
        elif not forceRawCalc and 'Parameters' in os.listdir(self.directory):
            parDir = os.path.join(self.directory, 'Parameters')
            parFiles = os.listdir(parDir)
            for parFile in parFiles:
                # remove the extension
                fname = os.path.splitext(parFile)[0]
                # get the bike and the parameter set type
                bike, ptype = space_out_camel_case(fname, output='list')
                # load the parameters
                pathToFile = os.path.join(parDir, parFile)
                self.parameters[ptype] = load_parameter_text_file(pathToFile)
        else:
            print "Where's the data?"

    def save(self, filetype='text'):
        '''
        Saves all the parameters to file.

        filetype : string
            'pickle' : python pickled dictionary
            'matlab' : matlab .mat file
            'text' : comma delimited text file

        '''

        if filetype == 'pickle':
            for k, v in self.params.items():
                thefile = self.directory + self.shortname + k + '.p'
                f = open(thefile, 'w')
                pickle.dump(v, f)
                f.close()
        elif filetype == 'matlab':
            # this should handle the uncertainties properly
            print "Doesn't work yet"

        elif filetype == 'text':
            print "Doesn't work yet"

    def calculate_from_measured(self, forcePeriodCalc=False):
        '''Calculates the parameters from measured data.

        '''
        rawDataDir = os.path.join(self.directory, 'RawData')
        pathToFile = os.path.join(rawDataDir, self.shortname + 'Measured.txt')

        # load the measured parameters
        mp = load_parameter_text_file(pathToFile)

        # if the the user doesn't specifiy to force period calculation, then
        # see if enough data is actually available in the Measured.txt file to
        # do the calculations
        if not forcePeriodcalc:
            # check to see if mp contains at enough periods to not need
            # recalculation
            ncTSum = 0
            ntTSum = 0
            isForkSplit = False
            for key in mp.keys():
                if key[:2] == 'Tc':
                    ncTSum += 1
                elif key[:2] == 'Tt':
                    ntTSum += 1
                # if there is an 'S' then the fork is split in two parts
                if key[2] == 'S' or key[1] == 'S':
                    isForkSplit = True

            # if there isn't enough data then force the period cals again
            if isForkSplit:
                if ncTSum < 5 and ntTSum < 11:
                    forcPeriodCalc = True
            else:
                if ncTSum < 4 and ntTSum < 8:
                    forcePeriodCalc = True

        if forcePeriodCalc == True:
            matFiles = [x for x in os.listdir(rawDataDir) if
                        x.endswith('.mat')]


        for k, v in ddU.items():
            if k[-1] == 'T' and v == None:
                print k
                # then this is a period that has no value, so we should
                # calculate it from the oscillation data
                body, pendulum = space_out_camel_case(k[:-1]).strip().split(' ')
                # now find the files that matches
                Tdict = {}
                for f in os.listdir(self.directory):
                    flist = space_out_camel_case(f[:-2]).strip().split(' ')
                    # now you have [bike, body, pend, angle, measurement]
                    bikematch = self.shortname == flist[0]
                    bodymatch = body.capitalize() == flist[1]
                    try:
                        pendmatch = pendulum == flist[2]
                    except:
                        pendmatch = False
                    if bikematch and bodymatch and pendmatch:
                        try:
                            Tdict[flist[3][:-1]].append(flist[3][-1])
                        except:
                            Tdict[flist[3][:-1]] = [flist[3][-1]]
                    # now you have something like:
                    # Tdict = {'First':['1','2','3'],
                    #          'Second':['1','2','3'],
                    #          'Third':['1','2','3']}
                for k, v in Tdict.items():
                    Tdict[k] = len(v)
                print Tdict

        # calculate all the benchmark parameters
        par = {}

        # calculate the wheel radii
        par['rR'] = ddU['rearWheelDist']/2./pi/ddU['rearWheelRot']
        par['rF'] = ddU['frontWheelDist']/2./pi/ddU['frontWheelRot']

        # steer axis tilt in radians
        par['lambda'] = pi/180.*(90. - ddU['headTubeAngle'])

        # calculate the front wheel trail
        forkOffset = ddU['forkOffset']
        par['c'] = (par['rF']*unumpy.sin(par['lambda'])
                      - forkOffset)/unumpy.cos(par['lambda'])

        # wheelbase
        par['w'] = ddU['wheelbase']

        # calculate the frame rotation angle
        # alpha is the angle between the negative z pendulum (horizontal) and the
        # positive (up) steer axis, rotation about positive y
        alphaFrame = ddU['frameAngle']
        # beta is the angle between the x bike frame and the x pendulum frame, rotation
        # about positive y
        betaFrame = par['lambda'] - alphaFrame*np.pi/180

        # calculate the slope of the CoM line
        frameM = -unumpy.tan(betaFrame)

        # calculate the z-intercept of the CoM line
        # frameMassDist is positive according to the pendulum ref frame
        frameMassDist = ddU['frameMassDist']
        cb = unumpy.cos(betaFrame)
        frameB = -frameMassDist/cb - par['rR']

        # calculate the fork rotation angle
        betaFork = par['lambda'] - ddU['forkAngle']*np.pi/180.

        # calculate the slope of the fork CoM line
        forkM = -unumpy.tan(betaFork)

        # calculate the z-intercept of the CoM line
        forkMassDist = ddU['forkMassDist']
        cb = unumpy.cos(betaFork)
        tb = unumpy.tan(betaFork)
        forkB = - par['rF'] - forkMassDist/cb + par['w']*tb

        # intialize the matrices for the center of mass locations
        frameCoM = zeros((2), dtype='object')
        forkCoM = zeros((2), dtype='object')

        comb = np.array([[0, 1], [0, 2], [1, 2]])
        # calculate the frame center of mass position
        # initialize the matrix to store the line intersections
        lineX = zeros((3, 2), dtype='object')
        # for each line intersection...
        for j, row in enumerate(comb):
            a = unumpy.matrix(np.vstack([-frameM[row], np.ones((2))]).T)
            b = frameB[row]
            lineX[j] = np.dot(a.I, b)
        frameCoM[:] = np.mean(lineX, axis=0)
        # calculate the fork center of mass position
        # reinitialize the matrix to store the line intersections
        lineX = zeros((3, 2), dtype='object')
        # for each line intersection...
        for j, row in enumerate(comb):
            a = unumpy.matrix(np.vstack([-forkM[row], np.ones((2))]).T)
            b = forkB[row]
            lineX[j] = np.dot(a.I, b)
        forkCoM[:] = np.mean(lineX, axis=0)

        par['xB'] = frameCoM[0]
        par['zB'] = frameCoM[1]
        par['xH'] = forkCoM[0]
        par['zH'] = forkCoM[1]

        return par

def select_good_data(data, percent):
    '''Returns a slice of the data from the maximum value to a percent of the
    max.

    Parameters
    ----------
    data : ndarray, shape(1,)
        This should be a decaying function.
    percent : float
        The percent of the maximum to clip.

    '''
    maxVal = np.max(np.abs(data))
    maxInd = np.argmax(np.abs(data))
    #for i, v in reversed(list(enumerate(data))):

def average_rectified_sections(data):
    data = data - np.mean(data)
    # find the zero crossings
    zero_crossings = np.where(np.diff(np.sign(data)))[0]
    crossings = np.concatenate(0, np.append(zero_crossings, len(data) - 1))
    secMean = []
    localMeanInd = []
    for sec in np.split(data, zero_crossings):
        localMeanInd.append(np.argmax(sec))
        secMean.append(np.mean(sec))
    meanInd = []
    for val in meanInd:
        meanInd.append(crossings[i] + localMeanInd)
    return meanInd, secMean

def fit_data(filename):
    '''
    Returns the period and uncertainty for a decaying oscillation.

    Parameters
    ----------
    filename : string
        directory + filename of the pickled data file

    Returns
    -------
    T : ufloat
        the period of oscillation and its uncertainty

    '''
    df = open(filename)
    pendDat = pickle.load(df)
    df.close()
    y = pendDat['data'].ravel()
    time = pendDat['duration']
    x = np.linspace(0, time, num=len(y))
    # decaying oscillating exponential function
    fitfunc = lambda p, t: p[0] + np.exp(-p[3]*p[4]*t)*(p[1]*np.sin(p[4]*np.sqrt(1-p[3]**2)*t) + p[2]*np.cos(p[4]*np.sqrt(1-p[3]**2)*t))
    # initial guesses
    p0 = np.array([1.35, -.5, -.75, 0.01, 3.93])
    # create the error function
    errfunc = lambda p, t, y: fitfunc(p, t) - y
    # minimize the error function
    p1, success = op.leastsq(errfunc, p0[:], args=(x, y))
    # plot the fitted curve
    lscurve = fitfunc(p1, x)
    rsq, SSE, SST, SSR = fit_goodness(y, lscurve)
    sigma = np.sqrt(SSE/(len(y)-len(p0)))
    # calculate the jacobian
    L = jac_fitfunc(p1, x)
    # the Hessian
    H = np.dot(L.T, L)
    # the covariance matrix
    U = sigma**2.*np.linalg.inv(H)
    # the standard deviations
    sigp = np.sqrt(U.diagonal())
    # frequency and period
    wo = ufloat((p1[4], sigp[4]))
    zeta = ufloat((p1[3], sigp[3]))
    wd = (1. - zeta**2.)**(1./2.)*wo
    f = wd/2./np.pi
    # return the period
    return 1./f

def jac_fitfunc(p, t):
    '''
    Calculate the Jacobian of a decaying oscillation function.

    Uses the analytical formulations of the partial derivatives.

    Parameters:
    -----------
    p : the five parameters of the equation
    t : time vector

    Returns:
    --------
    jac : The jacobian, the partial of the vector function with respect to the
    parameters vector. A 5 x N matrix where N is the number of time steps.

    '''
    jac = zeros((len(p), len(t)))
    e = np.exp(-p[3]*p[4]*t)
    dampsq = np.sqrt(1 - p[3]**2)
    s = np.sin(dampsq*p[4]*t)
    c = np.cos(dampsq*p[4]*t)
    jac[0] = ones_like(t)
    jac[1] = e*s
    jac[2] = e*c
    jac[3] = -p[4]*t*e*(p[1]*s + p[2]*c) + e*(-p[1]*p[3]*p[4]*t/dampsq*c
            + p[2]*p[3]*p[4]*t/dampsq*s)
    jac[4] = -p[3]*t*e*(p[1]*s + p[2]*c) + e*dampsq*t*(p[1]*c - p[2]*s)
    return jac.T

def fit_goodness(ym, yp):
    '''
    Calculate the goodness of fit.

    Parameters:
    ----------
    ym : vector of measured values
    yp : vector of predicted values

    Returns:
    --------
    rsq: r squared value of the fit
    SSE: error sum of squares
    SST: total sum of squares
    SSR: regression sum of squares

    '''
    SSR = sum((yp - np.mean(ym))**2)
    SST = sum((ym - np.mean(ym))**2)
    SSE = SST - SSR
    rsq = SSR/SST
    return rsq, SSE, SST, SSR

def space_out_camel_case(s, output='string'):
        """Adds spaces to a camel case string.  Failure to space out string
        returns the original string.

        Examples
        --------
        >>> space_out_camel_case('DMLSServicesOtherBSTextLLC')
        'DMLS Services Other BS Text LLC'
        >>> space_out_camel_case('DMLSServicesOtherBSTextLLC', output='list')
        ['DMLS', 'Services', 'Other', 'BS', 'Text', 'LLC']

        """
        if output == 'string':
            return re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', ' ',
                          s).strip()
        elif output == 'list':
            string = re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', ' ',
                            s).strip()
            return string.split(' ')
        else:
            raise ValueError

def filename_to_dict(filename):
    '''Returns a dictionay of values based on the pendulum data file name.

    '''
    o = space_out_camel_case(os.path.splitext(filename)[0], output='list')
    # this only accounts for single digit trial numbers
    trial = o[-1][-1]
    o[-1] = o[-1][:-1]
    o.append(trial)
    breakdown = ['bicycle', 'part', 'pendulum', 'angleOrder', 'trial']
    dat = {}
    for word, val  in zip(breakdown, o):
        dat[word] = val
    return dat

def load_parameter_text_file(pathToFile):
    '''Returns a dictionary of ufloat parameters from a parameter file.

    Parameters
    ----------
    pathToFile : string
        The path to the text file with the parameters listed in the specified
        format.

    Returns
    -------
    parameters : dictionary

    For example:

    'c = 0.08 +/- 0.01\nd=0.314+/-0.002\nt = 0.1+/-0.01, 0.12+/-0.02'

    The first item on the line must be the variable name and the second is an
    equals sign. The values to the right of the equal sign much contain an
    uncertainty and multiple comma seperated values will be averaged.

    '''

    f = open(pathToFile, 'r')
    parameters = {}
    # parse the text file
    for line in f:
        if line[0] != '#':
            # remove any whitespace characters and split into a list
            equality = line.strip().split('=')
            # ['a ', ' 0.1 +/- 0.05 , 0.09 +/- 0.05']
            vals = equality[1].strip().split(',')
            # ['0.1 +/- 0.05 ', ' 0.09 +/- 0.05']
            ufloats = [ufloat(x) for x in vals]
            parameters[equality[0].strip()] = np.mean(ufloats)

    return parameters

def load_pendulum_data_mat_file(pathToFile):
    '''Returns a dictionay containing the data from the pendulum data mat file.

    '''
    pendDat = {}
    loadmat(pathToFile, mdict=pendDat)
    #clean up the matlab imports
    del(pendDat['__globals__'], pendDat['__header__'], pendDat['__version__'])
    for k, v in pendDat.items():
        try:
            #change to an ascii string
            pendDat[k] = v[0].encode('ascii')
        except:
            #if an array of a single number
            if np.shape(v)[0] == 1:
                pendDat[k] = v[0][0]
            #else if the notes are empty
            elif np.shape(v)[0] == 0:
                pendDat[k] = ''
            #else it is the data which needs to be a one dimensional array
            else:
                pendDat[k] = v.reshape((len(v),))
    return pendDat

