import os, gc
import subprocess as sp

class inputfile:
    def __init__(self,fname):
        self.name = fname
        self.path = os.path.abspath(fname)
        self.length = pdflength(self.path)

class intermediatefile:
    def __init__(self,fname,root='.'):
        self.name = fname
        self.path = os.path.abspath(os.path.join(root,fname))

    def __del__(self):
        os.remove(self.path)

def pdflength(fname):
    p = sp.Popen(['pdfinfo',fname],stdout=sp.PIPE)
    so = p.stdout.readlines()
    lines = ["".join(chr(int(a)) for a in b).split() for b in so]
    for line in lines:
        if line[0]=='Pages:':
            L = int(line[1])
            break
    return L

def extract_page(fname,pagenum):
    args = 'pdfseparate -f {:d} -l {:d} {:s} page%d.pdf'.format(pagenum,pagenum,fname).split(' ')
    p = sp.Popen(args)
    p.wait()
    pagename = 'page{:d}.pdf'.format(pagenum+1)
    return intermediatefile(pagename)

def convert_page_to_png(pdffile,density):
    pngfile = intermediatefile(pdffile.path[:-4]+'.png')
    cmd = 'convert -density {:d}x{:d} {:s} {:s}'
    args = cmd.format(density,density,pdffile.path,pngfile.path).split(' ')
    p = sp.Popen(args)
    p.wait()
    return pngfile
    
def ocrify(fname,outputbase):
    args = 'tesseract {:s} {:s} pdf'.format(fname,outputbase).split(' ')
    p = sp.Popen(args)
    p.wait()
    return intermediatefile(outputbase+'.pdf'), intermediatefile(outputbase+'.txt')

def pdfjoin(pages,outfile):
    args = ['pdfjoin']+pages+['-o',outfile]
    p = sp.Popen(args)
    p.wait()
    return outfile

def main(pdffile,density):
    files = []
    plaintexts = []
    for n in range(pdffile.length):
        print("Converting page ",n)
        pdfpage = extract_page(pdffile.name,n)
        pngpage = convert_page_to_png(pdfpage,density)
        ocr_pdf,ocr_txt = ocrify(pngpage.path,pngpage.path[:-4]+"_ocr")
        plaintexts.append(ocr_txt)
        files.append(ocr_pdf)
    pages = [_.name for _ in files]
    outfile = pdffile.name[:-4]+'_ocr.pdf'
    out = pdfjoin(pages,outfile)
    with open(outfile[:-3]+'txt','w') as f:
        p = sp.Popen(['cat']+[_.path for _ in plaintexts],stdout=f)
        p.wait()
    print("Done! Output sent to ",outfile)
    return out

if __name__=='__main__':
    import sys
    main(inputfile(sys.argv[-1]),int(200))
