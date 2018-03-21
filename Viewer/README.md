# DisplacedDimuon Plot Viewer

Place

  * `script.js`
  * `styles.css`
  * `viewer.html`

in a folder called `viewer/`.

Place all `*.png` files in `viewer/img/png`, along with a `viwer/img/error.png`.

I will treat the `DisplacedDimuons/Analysis/plotters/pngs/` folder as the main source.

To move files to the CERN website,

```bash
rsync -vruc --delete ~/DDAnalysis/plotters/pngs/* ~/www/viewer/img/png/
```
To move files to my Mac's local directory (which I use for testing),

```bash
rsync -vruc --delete $CH:~/DDAnalysis/plotters/pngs/* ~/code/viewer/img/png/
```
