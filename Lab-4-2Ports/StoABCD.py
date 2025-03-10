import skrf as rf
import numpy as np
import matplotlib.pyplot as plt
#------Variables-------
# epseff = 1.87
epseff = 1.9146
    #effective relative permittivity
l = 20e-3
    #length [m]
c0 = 3e8
    #light velocity free space [m/s]
# Z0 = 51.19
Z0 = 50.59

#------Functions------
def getABCDGap(ABCDline, ABCDtotal):
    #Works the same as with a loop

    ABCDline_inverted = np.linalg.inv(ABCDline)

    ABCDgap = ABCDline_inverted @ ABCDtotal @ ABCDline_inverted

    return ABCDgap


def getABCDLine(fRange, Z0):

    ABCDline = np.zeros((len(fRange), 2, 2), dtype=complex)

    Y0 = 1/Z0

    for i, f in enumerate(fRange):

        ω = 2*np.pi*f
        β = (ω*np.sqrt(epseff))/c0

        A = np.cos(β*l)
        B = 1j*Z0*np.sin(β*l)
        C = 1j*Y0*np.sin(β*l)
        D = np.cos(β*l)

        ABCDline[i,:,:] = np.array([[A,B],[C,D]])

    return ABCDline

def ReadTXT(Path):
    frequency = []
    real_part = []
    imaginary_part = []

    # Open the file and read line by line
    with open(Path, 'r') as file:
        # Skip the header lines (first two lines)
        next(file)  # Skip the first line (header)
        next(file)  # Skip the second line (separator)

        # Process each line in the file
        for line in file:
            # Skip lines that start with '#' or are empty
            if line.strip().startswith('#') or not line.strip():
                continue

            # Split the line into columns based on whitespace
            columns = line.split()

            # Ensure the line has exactly 3 columns (frequency, real, imaginary)
            if len(columns) >= 2 :
                # Append the values to the respective lists
                frequency.append(float(columns[0].replace(",", ".")))
                real_part.append(float(columns[1].replace(",", ".")))
                if len(columns) >= 3:
                    imaginary_part.append(float(columns[2].replace(",", ".")))


    return np.array(frequency), np.array(real_part), np.array(imaginary_part)

def prepareSMatrix(s11Real, s11Imag, s12Real, s12Imag):

    #Output: fully prepared S matrix from the 2x2 matrix parameters.

    entries = len(s11Real)
    S = np.zeros((entries,2,2),dtype=complex)

    s11 = s11Real + 1j * s11Imag
    s12 = s12Real + 1j * s12Imag
    s21 = s12
    s22 = s11

    for i in range(entries):
        Si = np.array([[s11[i], s12[i]],[s21[i], s22[i]]])
        S[i,:,:] = Si

    return S
def plotAB(ABCD):
    A = ABCD[:, 0, 0]  # A is the (0, 0) element
    B = ABCD[:, 0, 1]  # B is the (0, 1) element

    # Plotting
    plt.figure(figsize=(12, 4))

    # Plot real and imaginary parts of A_gap
    # plt.plot(fRange*1e-9, np.real(A), label='Real(A_gap)', color='blue')
    # plt.plot(fRange*1e-9, np.imag(A), label='Imag(A_gap)', linestyle='--', color='blue')

    # Plot real and imaginary parts of B_gap
    plt.plot(fRange * 1e-9, np.real(B), label='Real(B_gap)', color='green')
    plt.plot(fRange * 1e-9, np.imag(B), label='Imag(B_gap)', linestyle='--', color='green')
    plt.xlim(5,10)

    # Adding labels and title
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Value')
    plt.title('Real and Imaginary Parts of B vs Frequency')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("A1_B_realimag")
    # Show plot
    plt.show()

    return

def PlotCpCg(Cg_list, Cp_list, fRange):
    # Plotting
    plt.figure(figsize=(12, 4))

    # Plot Cp vs frequency
    plt.plot(fRange*1e-9, Cp_list*1e12, label='Cp', color='blue', linestyle='--')

    # Plot Cg vs frequency
    # plt.plot(fRange*1e-9, Cg_list*1e12, label='Cg', color='green', linestyle='--')

    # Adding labels and title
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Capacitance (pF)')
    plt.title('Cp vs Frequency')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # plt.ylim(20,70)
    plt.xlim(5,10)
    plt.savefig("B_halfmm_Cp_plot")

    # Show plot
    plt.show()

    return


def getCapacitances(ABCDgap, fRange):

    A = ABCDgap[:,0,0]
    B = ABCDgap[:,0,1]

    Zg = B

    Zp = Zg/(A-1)

    # print(Zg)
    # print(Zp)
    Cg_list = np.real(1/(1j*fRange*2*np.pi*Zg))
    Cp_list = np.real(1/(1j*fRange*2*np.pi*Zp))

    Cg = sum(Cg_list)/len(Cg_list)
    Cp = sum(Cp_list)/len(Cp_list)

    return Cg, Cp, Cg_list, Cp_list


if __name__ == '__main__':

    #Get the values for the S11
    fRange, S11Real, S11Imag = ReadTXT("3Ds11_kleineregap.txt")
    _ , S12Real, S12Imag = ReadTXT("3Ds12_kleineregap.txt")

    fRange *= 1e9 #convert to GHz

    print(fRange)

    S = prepareSMatrix(S11Real, S11Imag, S12Real, S12Imag)

    ABCDtotal = rf.network.s2a(S, Z0)

    ABCDline = getABCDLine(fRange, Z0)

    ABCDgap = getABCDGap(ABCDline, ABCDtotal)

    # plotAB(ABCDtotal)

    Cg, Cp, Cg_list, Cp_list = getCapacitances(ABCDgap, fRange)
    #
    PlotCpCg(Cg_list, Cp_list, fRange)
    #
    print(f"Cg = {Cg}, Cp = {Cp}")

