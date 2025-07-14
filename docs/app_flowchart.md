flowchart TD
  A[User visits site]
  A-->B[Auth check]
  B-->C{Authenticated?}
  C-->|No|D[LoginSignup]
  C-->|Yes|E[Dashboard]
  E-->F{Existing book?}
  F-->|New|G[Create Book Draft]
  F-->|Edit|H[Select Book]
  G-->I[Character Builder]
  H-->I
  I-->J[Plot Composer]
  J-->K[Review Story]
  K-->L{Approve Story?}
  L-->|No|O[Flag for Parent]
  L-->|Yes|M[Text Moderation]
  M-->N{Passed?}
  N-->|No|O
  N-->|Yes|P[Image Generation]
  P-->Q[Image Moderation]
  Q-->R{Passed?}
  R-->|No|O
  R-->|Yes|S[Assemble Flipbook]
  S-->T[Flipbook Reader]
  T-->U[PDF Export]
  U-->V[Notify via EmailSMS]
  V-->W[LibraryVersioning]