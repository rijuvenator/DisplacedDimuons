//======================macro Rebin.C==============================
TH1F *Rebin(TH1F *hold, const Int_t ngroup)
{
//   example of ROOT macro to rebin a 1-D histogram hold
// Method:
//   a new temporary histogram hnew is created and return to the caller
//   The parameter ngroup indicates how many bins of hold have to me
//merged
//   into one bin of hnew
//   Errors are not taken into account
//
// Usage:
//   Root > .L rebin.C;  //load this macro
//   Root > TH1F *hnew = Rebin(hold,2); //to rebin hold grouping 2 bins
//in one
//
//   This macro will become a new TH1 function (taking care of errors)
//       TH1 *TH1::Rebin(const Int_t ngroup)

   TAxis *xold   = hold->GetXaxis();
   Int_t nbins   = xold->GetNbins();
   Float_t xmin  = xold->GetXmin();
   Float_t xmax  = xold->GetXmax();
   if ((ngroup <= 0) || (ngroup > nbins)) {
      printf("ERROR in Rebin. Illegal value of ngroup=%d\n",ngroup);
      return 0;
   }
   Int_t newbins = nbins/ngroup;

   // create a clone of the old histogram
   TH1F *hnew = (TH1F*)hold->Clone();

   // change name and axis specs
   hnew->SetName("hnew");
   TAxis *xnew   = hnew->GetXaxis();
   xnew->Set(newbins,xmin,xmax);
   hnew->Set(newbins+2);

   // copy merged bin contents (ignore under/overflows)
   Int_t bin, i;
   Int_t oldbin = 1;
   Stat_t bincont;
   for (bin = 1;bin<=newbins;bin++) {
      bincont = 0;
      for (i=0;i<ngroup;i++) {
         bincont += hold->GetBinContent(oldbin+i);
      }
      hnew->SetBinContent(bin,bincont);
      oldbin += ngroup;
   }

   return hnew;
}
