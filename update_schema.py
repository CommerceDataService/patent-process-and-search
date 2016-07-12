from s3_upload.solr import Solr

solr = Solr('http://52.90.109.169:8983', 'oadata_3_shard1_replica1')


longs = (
    "appl_id",
)

doubles = (
  "file_dt",
  "effective_filing_dt",
  "dn_nsrd_curr_loc_dt",
  "app_status_dt",
  "patent_issue_dt",
  "abandon_dt",
  "doc_date",
)

text = (
   "invn_ttl_tx",
)

strings = (
    "type",
    "appid",
    "ifwnumber",
    "documentcode",
    "documentsourceidentifier",
    "partyidentifier",
    "groupartunitnumber",
    "inv_subj_matter_ty",
    "appl_ty",
    "dn_examiner_no",
    "dn_dw_dn_gau_cd",
    "dn_pto_art_class_no",
    "dn_pto_art_subclass_no",
    "confirm_no",
    "dn_intppty_cust_no",
    "atty_dkt_no",
    "dn_nsrd_curr_loc_cd",
    "app_status_no",
    "wipo_pub_no",
    "patent_no",
    "disposal_type",
    "se_in",
    "pct_no",
    "aia_in",
    "continuity_type",
    "frgn_priority_clm",
    "usc_119_met",
    "fig_qt",
    "indp_claim_qt",
    "efctv_claims_qt",
    "staging_src_path",
)


for f in longs:
    solr.add_field(f, 'tlongs')

for f in doubles:
    solr.add_field(f, 'tdoubles')

for f in strings:
    solr.add_field(f, 'string')

for f in text:
    solr.add_field(f, 'text')
