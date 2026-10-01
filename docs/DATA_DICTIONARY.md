# Data dictionary

Key processed files and their columns. Machine-readable version: `docs/data_dictionary.csv` (also shown in the dashboard).

## `municipality_election_panel_2000_2021.csv`

| Column | Meaning | Unit |
|---|---|---|
| `MuniCode` | Analytical municipality code (33 present-day units) | code |
| `Year` | Local Government Election year | year |
| `RegisteredVoters` | Registered voters, counted once per voting district | persons |
| `ValidVotes` | Valid PR-ballot votes (sum of party votes) | votes |
| `SpoiltVotes` | Spoilt PR ballots, counted once per voting district | votes |
| `VotesCast` | ValidVotes + SpoiltVotes | votes |
| `Turnout_%` | 100 x VotesCast / RegisteredVoters | % |
| `SpoiltRate_%` | 100 x SpoiltVotes / VotesCast | % |
| `TopShare_%` | PR share of the largest party | % |
| `Margin_pts` | Largest minus second-largest PR share | percentage points |
| `ENP` | Effective number of parties, 1/sum(p_i^2), full party distribution | parties |
| `NumberOfParties` | Parties receiving PR votes in the municipality | count |
| `Previous*` | Same quantity in the previous LGE for that municipality | various |
| `RegistrationGrowth_%` | Change in registered voters since the previous LGE | % |

## `party_shares_selected_wide_2000_2021.csv`

| Column | Meaning | Unit |
|---|---|---|
| `ANC, DA, EFF, UDM, ATM` | PR vote share of each named party | % |
| `OTHER` | 100 minus the five named parties | % |

## `master_panel_2000_2021.csv`

| Column | Meaning | Unit |
|---|---|---|
| `ProvincialLevel_%` | Unweighted mean municipal turnout in that election | % |
| `RelativeTurnout_pts` | Turnout_% minus ProvincialLevel_% | percentage points |
| `Prev_<party>, Swing_<party>` | Previous-election share and change in share | % / points |
| `Pop, U15, O65, Med, NoSch, Matric, Higher, Formal, Water, Elec` | Census indicators, DESCRIPTIVE policy (2011 observed; 2016/2021 interpolated to 2022) | various |
| `K_<indicator>` | Census indicators, AS-KNOWN policy (latest census published before the election) | various |

## `municipality_scenarios_2026.csv`

| Column | Meaning | Unit |
|---|---|---|
| `Relative_2026_pts` | Modelled relative turnout position for 2026 (relative persistence) | percentage points |
| `Turnout_<Scenario>_%` | Scenario turnout = assumed provincial level + Relative_2026_pts | % |
| `TurnoutBand_pts` | 80th percentile of historical absolute municipal errors (excludes provincial-level uncertainty) | percentage points |
| `ExpectedVotes_<Scenario>` | Scenario turnout x registered voters (basis in RegistrationBasis) | votes |
| `<party>_Validated_%` | PR share under the validated methods (status quo) | % |
| `<party>_Trend_%` | PR share if each party's 2016-2021 swing repeats (not validated) | % |
| `Validated_Leader / Gap_pts / Status` | Largest category, lead over runner-up, and 'Too close to call' if lead < 2 x party MAE | category / points |
| `SwingNeeded_pts` | Uniform swing from leader to runner-up that would change the largest category | percentage points |

## Municipality codes

| Code | Municipality | District |
|---|---|---|
| BUF | Buffalo City | Buffalo City (metro) |
| EC101 | Dr Beyers Naude | Sarah Baartman |
| EC102 | Blue Crane Route | Sarah Baartman |
| EC104 | Makana | Sarah Baartman |
| EC105 | Ndlambe | Sarah Baartman |
| EC106 | Sundays River Valley | Sarah Baartman |
| EC108 | Kouga | Sarah Baartman |
| EC109 | Kou-Kamma | Sarah Baartman |
| EC121 | Mbhashe | Amathole |
| EC122 | Mnquma | Amathole |
| EC123 | Great Kei | Amathole |
| EC124 | Amahlathi | Amathole |
| EC126 | Ngqushwa | Amathole |
| EC129 | Raymond Mhlaba | Amathole |
| EC131 | Inxuba Yethemba | Chris Hani |
| EC135 | Intsika Yethu | Chris Hani |
| EC136 | Emalahleni | Chris Hani |
| EC137 | Engcobo | Chris Hani |
| EC138 | Sakhisizwe | Chris Hani |
| EC139 | Enoch Mgijima | Chris Hani |
| EC141 | Elundini | Joe Gqabi |
| EC142 | Senqu | Joe Gqabi |
| EC145 | Walter Sisulu | Joe Gqabi |
| EC153 | Ngquza Hill | O.R. Tambo |
| EC154 | Port St Johns | O.R. Tambo |
| EC155 | Nyandeni | O.R. Tambo |
| EC156 | Mhlontlo | O.R. Tambo |
| EC157 | King Sabata Dalindyebo | O.R. Tambo |
| EC441 | Matatiele | Alfred Nzo |
| EC442 | Umzimvubu | Alfred Nzo |
| EC443 | Winnie Madikizela-Mandela | Alfred Nzo |
| EC444 | Ntabankulu | Alfred Nzo |
| NMA | Nelson Mandela Bay | Nelson Mandela Bay (metro) |
