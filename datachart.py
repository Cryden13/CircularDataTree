from matplotlib.colors import Colormap
import matplotlib.pyplot as plt
from typing import Union as U
from io import BytesIO
from PIL import Image


class DataBuilder:
    sizes: list[int]
    lbls: list[str]
    cmap: Colormap
    args: tuple[str, U[int, float], U[int, float], U[int, float]]

    def __init__(self, fontfamily, fontsize, distance, radius):
        self.sizes = list()
        self.lbls = list()
        self.args = (fontfamily, fontsize, distance, radius)

    def setColormap(self, lout: int, cm: Colormap, offset: U[int, float]):
        out = list()
        for step in self.sizes:
            out.append(offset if offset >= 0 else (lout + offset))
            offset += step
        self.cmap = cm(out)

    def getkwargs(self):
        ffam, fsize, dist, rad = self.args
        return dict(
            labels=self.lbls,
            labeldistance=dist,
            rotatelabels=True,
            startangle=90,
            textprops=dict(family=ffam,
                           size=fsize,
                           ha='center',
                           va='center'),
            radius=rad,
            colors=self.cmap,
            wedgeprops=dict(width=0.5,
                            edgecolor='black',
                            linewidth=0.5),
            counterclock=False)


class DataChart(Image.Image):
    """This class is a PIL.Image.Image of a circular datatree"""
    _inr: DataBuilder
    _mid: DataBuilder
    _out: DataBuilder

    def __init__(self, dataset: dict[str, dict[str, list[str]]],
                 colormap_name: str = "hsv", offset: U[int, float] = 20,
                 fontfamily: str = "Ebrima", fontsize: tuple[U[int, float], U[int, float], U[int, float]] = (8, 7, 6.5)):
        """\
        Parameters
        ----------
        dataset : dict
            the data to turn into a circular datatree. {category: {subcategory: [*items]}}
        colormap_name : str, optional (default is "hsv")
            the name of a matplotlib.colors.Colormap
        offset : int | float, optional (default is 20)
            the color offset for the middle and outer rings. Must be positive
        fontfamily : str, optional (default is "Ebrima")
            the font family to use for labels
        fontsize : tuple, optional (default is (8, 7, 6.5))
            the font size to use for labels. (inner, mid, outer)
        """
        Image.Image.__init__(self)
        self._inr = DataBuilder(fontfamily, fontsize[0],
                                distance=0.6, radius=0.5)
        self._mid = DataBuilder(fontfamily, fontsize[1],
                                distance=0.77, radius=1)
        self._out = DataBuilder(fontfamily, fontsize[2],
                                distance=0.85, radius=1.5)
        self._setData(dataset)
        self._setColormaps(colormap_name, offset)
        self._buildChart()

        bimg = BytesIO()
        plt.savefig(bimg, dpi=300)
        img = Image.open(bimg).resize(size=(1440, 1440),
                                      box=(315, 55, 1655, 1395))
        for var in vars(img).keys():
            setattr(self, var, getattr(img, var))

    def _setData(self, dataset: dict[str, dict[str, list[str]]]):
        for iLbl, sub in dataset.items():
            iSize = 0
            for mLbl, outer in sub.items():
                mSize = 0
                for oLbl in outer:
                    self._out.sizes.append(1)
                    self._out.lbls.append(oLbl)
                    mSize += 1
                self._mid.sizes.append(mSize)
                self._mid.lbls.append(mLbl)
                iSize += mSize
            self._inr.sizes.append(iSize)
            self._inr.lbls.append(iLbl)

    def _setColormaps(self, cmapnm, offset):
        lout = len(self._out.sizes)
        cmap = plt.get_cmap(cmapnm, lout)
        offset = -round(lout/offset) if offset else 0
        self._out.setColormap(lout, cmap, offset)
        self._mid.setColormap(lout, cmap, offset)
        self._inr.setColormap(lout, cmap, 0)

    def _buildChart(self):
        figure, ax = plt.subplots()
        figure.patch.set_alpha(0)
        ax.pie(self._inr.sizes,
               **self._inr.getkwargs())
        ax.pie(self._mid.sizes,
               **self._mid.getkwargs())
        ax.pie(self._out.sizes,
               **self._out.getkwargs())
        ax.set(aspect='equal')


if __name__ == '__main__':
    from pathlib import Path
    from json import load
    pth = Path(__file__).parent.joinpath('dataset.json')
    with pth.open('r') as f:
        data = load(f)
    DataChart(data).show()
