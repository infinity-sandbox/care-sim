select top 10 'OPD', dateadd(mi,t7.Timezoneoffsetminutes,t2.EncodedDate) OrderDate, t3.RegistrationNo, 
t3.FirstName, t3.MiddleName, t3.LastName, t5.ServiceName, t4.FieldName, t1.ValueText, t6.unitname
from diaginvresultop t1
inner join diagsampleoplabmain t2 on t2.diagsampleid = t1.diagsampleid and t2.active = 1
inner join registration t3 on t3.id = t2.registrationid
inner join diagfields t4 on t4.fieldid = t1.fieldid and t4.FieldType = 'N'
inner join itemofservice t5 on t5.serviceid = t2.serviceid
inner join DiagUnitMaster t6 on t6.unitid = t1.unitid
inner join FacilityMaster t7 on t7.FacilityId = t2.FacilityId
where t1.active = 1



select top 10 'IPD', dateadd(mi,t7.Timezoneoffsetminutes,t2.EncodedDate) OrderDate, t3.RegistrationNo, 
t3.FirstName, t3.MiddleName, t3.LastName, t5.ServiceName, t4.FieldName, t1.ValueText, t6.unitname
from diaginvresultip t1
inner join diagsampleiplabmain t2 on t2.diagsampleid = t1.diagsampleid and t2.active = 1
inner join registration t3 on t3.id = t2.registrationid
inner join diagfields t4 on t4.fieldid = t1.fieldid and t4.FieldType = 'N'
inner join itemofservice t5 on t5.serviceid = t2.serviceid
inner join DiagUnitMaster t6 on t6.unitid = t1.unitid
inner join FacilityMaster t7 on t7.FacilityId = t2.FacilityId
where t1.active = 1


select top 10 {PD}, dateadd(mi,t7.Timezoneoffsetminutes,t2.EncodedDate) OrderDate, t3.RegistrationNo, 
t3.FirstName, t3.MiddleName, t3.LastName, t5.ServiceName, t4.FieldName, t1.ValueText, t6.unitname
from diaginvresult{P} t1
inner join diagsample{P}labmain t2 on t2.diagsampleid = t1.diagsampleid and t2.active = 1
inner join registration t3 on t3.id = t2.registrationid
inner join diagfields t4 on t4.fieldid = t1.fieldid and t4.FieldType = 'N'
inner join itemofservice t5 on t5.serviceid = t2.serviceid
inner join DiagUnitMaster t6 on t6.unitid = t1.unitid
inner join FacilityMaster t7 on t7.FacilityId = t2.FacilityId
where t1.active = 1



select top 20 'IPD', dateadd(mi,t7.Timezoneoffsetminutes,t2.EncodedDate) OrderDate, t3.RegistrationNo, t4.FieldName
from diaginvresultip t1
inner join diagsampleiplabmain t2 on t2.diagsampleid = t1.diagsampleid and t2.active = 1
inner join registration t3 on t3.id = t2.registrationid
inner join diagfields t4 on t4.fieldid = t1.fieldid and t4.FieldType = 'N'
inner join itemofservice t5 on t5.serviceid = t2.serviceid
inner join DiagUnitMaster t6 on t6.unitid = t1.unitid
inner join FacilityMaster t7 on t7.FacilityId = t2.FacilityId
where t1.active = 1 and t3.RegistrationNo = 200645072
order by dateadd(mi, t7.Timezoneoffsetminutes, t2.EncodedDate) desc;



select distinct t4.FieldName
from diaginvresultop t1
inner join diagsampleoplabmain t2 on t2.diagsampleid = t1.diagsampleid and t2.active = 1
inner join registration t3 on t3.id = t2.registrationid
inner join diagfields t4 on t4.fieldid = t1.fieldid and t4.FieldType = 'N'
inner join itemofservice t5 on t5.serviceid = t2.serviceid
inner join DiagUnitMaster t6 on t6.unitid = t1.unitid
inner join FacilityMaster t7 on t7.FacilityId = t2.FacilityId
where t1.active = 1
order by t4.FieldName;









-- sample
-- {PD} = 'OPD' or 'IPD'
-- {P} = 'op' or 'ip'
-- {REGISTRATIONNO} = 200645072
-- {FIELDNAME} = 'HbA1c'

-- FieldName (IP)                                                                  
-- ----------------------------------------------------------------------------------------------------
-- .Bleeding Time  (BT)1                                                                               
-- 24 Hour Urine Total Volume                                                                          
-- 25 HYDROXY VITAMIN D-TOTAL                                                                          
-- Absolute Basophil Count                                                                             
-- Absolute Eosinophil Count (AEC)                                                                     
-- Absolute Lymphocyte Count                                                                           
-- Absolute Monocyte Count                                                                             
-- Absolute Neutrophil Count (ANC)                                                                     
-- Activtd.Partial Thromboplastin Time (APTT) Control                                                  
-- Actvtd.Partial Thromboplastin Time (APTT) Patient                                                   
-- age                                                                                                 
-- Albumin                                                                                             
-- Alkaline Phosphatase                                                                                
-- ALPHA-FETOPROTEIN(AFP) TUMOR MARKER                                                                 
-- Ammonia (Plasma)*                                                                                   
-- Amylase                                                                                             
-- Amylase (Fluid)                                                                                     
-- ANTI CYCLIC CITRULLINATED PEPTIDE (ANTI CCP)                                                        
-- Anti Mullerian Hormone (AMH)                                                                        
-- ANTI THYROGLOBULIN (ANTI-TG)                                                                        
-- ANTI THYROID PROXIDASE                                                                              
-- Anti Thyroid Proxidase*                                                                             
-- Antibody to Hepatitis C Virus                                                                       
-- Antibody to HIV 1 & 2, p24 Antigen                                                                  
-- Ascitic/Peritoneal Albumin                                                                          
-- Ascitic/Peritoneal Fluid for Glucose                                                                
-- Atypical Cells                                                                                      
-- BETA HCG (CANCER MARKER)                                                                            
-- Bilirubin Conjugated (Bc)                                                                           
-- Bilirubin Total (TBil) Numeric                                                                      
-- Bilirubin Unconjugated (Bu)                                                                         
-- Blood Sugar (1 Hr.)                                                                                 
-- Blood Sugar (2 Hrs.)                                                                                
-- Blood Sugar (Fasting)                                                                               
-- BUN - Blood Urea Nitrogen                                                                           
-- CA 125                                                                                              
-- Calcium                                                                                             
-- CEA                                                                                                 
-- Chloride                                                                                            
-- Chloride (Serum/Plasma)                                                                             
-- Cholesterol-Total                                                                                   
-- CK / CPK (Creatine Kinase)                                                                          
-- CKMB                                                                                                
-- CORTISOL (AM)                                                                                       
-- CORTISOL (PM)                                                                                       
-- CORTISOL (RANDOM)                                                                                   
-- Creatinine                                                                                          
-- CREATININE KINASE MB MASS                                                                           
-- CRP - C Reactive Protein                                                                            
-- CSF Differential Count- Lymphocytes                                                                 
-- CSF Differential Count- Neutrophils                                                                 
-- CSF for Glucose                                                                                     
-- CSF for Protein                                                                                     
-- D- Dimer                                                                                            
-- DLC - Band Cells                                                                                    
-- DLC - Basophils                                                                                     
-- DLC - Blasts                                                                                        
-- DLC - Eosinophils                                                                                   
-- DLC - Lymphocytes                                                                                   
-- DLC - Metamyelocytes                                                                                
-- DLC - Monocytes                                                                                     
-- DLC - Myelocytes                                                                                    
-- DLC - Neutrophils                                                                                   
-- DLC - Promyelocytes                                                                                 
-- dTIBC                                                                                               
-- ESR (Erythrocyte Sed.Rate)                                                                          
-- FDP  (Fibrin Degradation Product)                                                                   
-- Ferritin                                                                                            
-- Fluid for Glucose                                                                                   
-- Fluid for Protein                                                                                   
-- Fluid Volume                                                                                        
-- FT3 - Free T3                                                                                       
-- FT4 - Free T4                                                                                       
-- G - 6 PD DEFICIENCY TEST *                                                                          
-- GGTP (GAMMA GT)                                                                                     
-- Glucose (2 Hour Post Prandial)                                                                      
-- Glucose (Fasting Blood Sugar / FBS)                                                                 
-- Glucose (RBS/Random Blood Sugar)                                                                    
-- Haemoglobin Estimation (Hb)                                                                         
-- HBA1C - Glycosylated Hemoglobin                                                                     
-- HCG - BETA SPECIFIC                                                                                 
-- HDL CHOLESTEROL                                                                                     
-- HEM                                                                                                 
-- Hepatitis A Virus (Anti-HAV IgM)                                                                    
-- Hepatitis B surface Antigen                                                                         
-- HEPATITIS B VIRUS SURFACE ANTIBODY{QUANT}                                                           
-- Hepatitis E Virus {Anti-HEV IgM}                                                                    
-- Iron                                                                                                
-- LDH                                                                                                 
-- LDH (Fluid)                                                                                         
-- LH- Leutenizing Hormone                                                                             
-- Lipase                                                                                              
-- Magnesium                                                                                           
-- Mantoux Test                                                                                        
-- MCH                                                                                                 
-- MCHC                                                                                                
-- MCV                                                                                                 
-- NT-proBNP*                                                                                          
-- PCV (Haematocrit)                                                                                   
-- Peritoneal Fluid - Diff. Count, Lymphocytes                                                         
-- Peritoneal Fluid - Diff. Count, Neutrophills                                                        
-- Phosphorus                                                                                          
-- Platelet Count                                                                                      
-- Pleural Fluid - Diff. Count, Lymphocytes                                                            
-- Pleural Fluid - Diff. Count, Neutorphils                                                            
-- Pleural Fluid for Glucose                                                                           
-- Pleural Fluid for LDH                                                                               
-- Pleural Fluid for Protein                                                                           
-- Potassium                                                                                           
-- Procalcitonin(PCT),Quantitavie                                                                      
-- Prolactin                                                                                           
-- Protein Total                                                                                       
-- Prothrombin Time (PT) Control                                                                       
-- Prothrombin Time (PT) INR Value                                                                     
-- Prothrombin Time (PT) Ratio                                                                         
-- Prothrombin Time Patient Value                                                                      
-- PSA Total (Prostate Specific Antigen)                                                               
-- PTH - INTACT                                                                                        
-- RBC Count (Red Blood Cell)                                                                          
-- RDW                                                                                                 
-- Reticulocyte Count                                                                                  
-- serum creatnine                                                                                     
-- SGOT (AST)                                                                                          
-- SGPT (ALT)                                                                                          
-- Sodium                                                                                              
-- test Himanshu                                                                                       
-- Testosterone, Total                                                                                 
-- TLC                                                                                                 
-- Total IgE                                                                                           
-- Total Leukocyte Count (TLC)                                                                         
-- Triglycerides                                                                                       
-- Troponin-I (Quantitative)                                                                           
-- TSH-Thyroid Stimulating Hormone                                                                     
-- UREA                                                                                                
-- Uric Acid                                                                                           
-- Urine Analysis - pH                                                                                 
-- Urine Analysis - Quantity                                                                           
-- Urine Analysis - Specific Gravity                                                                   
-- Urine Chloride (Spot)                                                                               
-- Urine Creatinine                                                                                    
-- Urine Creatinine.                                                                                   
-- Urine Microalbumin(n)                                                                               
-- Urine Potassium (Spot)                                                                              
-- Urine Protein                                                                                       
-- Urine Sodium (Spot)                                                                                 
-- Vitamin B12





-- FieldName (OP)                                                      
-- ----------------------------------------------------------------------------------------------------
-- 24 Hour Urine Total Volume                                                                          
-- 25 HYDROXY VITAMIN D-TOTAL                                                                          
-- Absolute Basophil Count                                                                             
-- Absolute Eosinophil Count (AEC)                                                                     
-- Absolute Lymphocyte Count                                                                           
-- Absolute Monocyte Count                                                                             
-- Absolute Neutrophil Count (ANC)                                                                     
-- Acetone Qualitative                                                                                 
-- Activtd.Partial Thromboplastin Time (APTT) Control                                                  
-- Actvtd.Partial Thromboplastin Time (APTT) Patient                                                   
-- age                                                                                                 
-- Albumin                                                                                             
-- Alkaline Phosphatase                                                                                
-- ALPHA-FETOPROTEIN(AFP) TUMOR MARKER                                                                 
-- Ammonia (Plasma)*                                                                                   
-- Amylase                                                                                             
-- Amylase (Fluid)                                                                                     
-- ANTI CYCLIC CITRULLINATED PEPTIDE (ANTI CCP)                                                        
-- Anti Mullerian Hormone (AMH)                                                                        
-- ANTI THYROGLOBULIN (ANTI-TG)                                                                        
-- ANTI THYROID PROXIDASE                                                                              
-- Anti Thyroid Proxidase*                                                                             
-- Antibody to Hepatitis C Virus                                                                       
-- Antibody to HIV 1 & 2, p24 Antigen                                                                  
-- Ascitic/Peritoneal Albumin                                                                          
-- Ascitic/Peritoneal Fluid for Glucose                                                                
-- Atypical Cells                                                                                      
-- BETA HCG (CANCER MARKER)                                                                            
-- Bilirubin Conjugated (Bc)                                                                           
-- Bilirubin Total (TBil) Numeric                                                                      
-- Bilirubin Unconjugated (Bu)                                                                         
-- Bleeding Time  (BT)                                                                                 
-- Blood Sugar (1 Hr.)                                                                                 
-- Blood Sugar (2 Hrs.)                                                                                
-- Blood Sugar (Fasting)                                                                               
-- BUN - Blood Urea Nitrogen                                                                           
-- CA 125                                                                                              
-- Calcium                                                                                             
-- CEA                                                                                                 
-- Chloride                                                                                            
-- Chloride (Serum/Plasma)                                                                             
-- Cholesterol-Total                                                                                   
-- CK / CPK (Creatine Kinase)                                                                          
-- CKMB                                                                                                
-- CORTISOL (AM)                                                                                       
-- CORTISOL (PM)                                                                                       
-- CORTISOL (RANDOM)                                                                                   
-- Creatinine                                                                                          
-- CREATININE KINASE MB MASS                                                                           
-- CRP - C Reactive Protein                                                                            
-- CSF Differential Count- Lymphocytes                                                                 
-- CSF Differential Count- Neutrophils                                                                 
-- CSF for Glucose                                                                                     
-- CSF for Protein                                                                                     
-- D- Dimer                                                                                            
-- DLC - Band Cells                                                                                    
-- DLC - Basophils                                                                                     
-- DLC - Blasts                                                                                        
-- DLC - Eosinophils                                                                                   
-- DLC - Lymphocytes                                                                                   
-- DLC - Metamyelocytes                                                                                
-- DLC - Monocytes                                                                                     
-- DLC - Myelocytes                                                                                    
-- DLC - Neutrophils                                                                                   
-- DLC - Promyelocytes                                                                                 
-- dTIBC                                                                                               
-- ESR (Erythrocyte Sed.Rate)                                                                          
-- Estradiol (E2)                                                                                      
-- FDP  (Fibrin Degradation Product)                                                                   
-- Ferritin                                                                                            
-- Ferritin - Covid                                                                                    
-- Fluid for Glucose                                                                                   
-- Fluid for Protein                                                                                   
-- Fluid Volume                                                                                        
-- FSH- Follicle Stimulating Hormone*                                                                  
-- FT3 - Free T3                                                                                       
-- FT4 - Free T4                                                                                       
-- G - 6 PD DEFICIENCY TEST *                                                                          
-- GGTP (GAMMA GT)                                                                                     
-- Glucose (2 Hour Post Prandial)                                                                      
-- Glucose (Fasting Blood Sugar / FBS)                                                                 
-- Glucose (RBS/Random Blood Sugar)                                                                    
-- GLUCOSE CHALLENGE TEST (GCT)                                                                        
-- Haemoglobin Estimation (Hb)                                                                         
-- HBA1C - Glycosylated Hemoglobin                                                                     
-- HCG - BETA SPECIFIC                                                                                 
-- HDL CHOLESTEROL                                                                                     
-- HEM                                                                                                 
-- Hepatitis A Virus (Anti-HAV IgM)                                                                    
-- Hepatitis B surface Antigen                                                                         
-- HEPATITIS B VIRUS SURFACE ANTIBODY{QUANT}                                                           
-- Hepatitis E Virus {Anti-HEV IgM}                                                                    
-- Iron                                                                                                
-- LDH                                                                                                 
-- LH- Leutenizing Hormone                                                                             
-- Lipase                                                                                              
-- Magnesium                                                                                           
-- Mantoux Test                                                                                        
-- MCH                                                                                                 
-- MCHC                                                                                                
-- MCV                                                                                                 
-- New123                                                                                              
-- NT-proBNP*                                                                                          
-- PCV (Haematocrit)                                                                                   
-- Peritoneal Fluid - Diff. Count, Lymphocytes                                                         
-- Peritoneal Fluid - Diff. Count, Neutrophills                                                        
-- Phosphorus                                                                                          
-- Platelet Count                                                                                      
-- Pleural Fluid - Diff. Count, Lymphocytes                                                            
-- Pleural Fluid - Diff. Count, Neutorphils                                                            
-- Pleural Fluid for Glucose                                                                           
-- Pleural Fluid for LDH                                                                               
-- Pleural Fluid for Protein                                                                           
-- Potassium                                                                                           
-- Procalcitonin(PCT),Quantitavie                                                                      
-- Prolactin                                                                                           
-- Protein Total                                                                                       
-- Prothrombin Time (PT) Control                                                                       
-- Prothrombin Time (PT) INR Value                                                                     
-- Prothrombin Time (PT) Ratio                                                                         
-- Prothrombin Time Patient Value                                                                      
-- PSA Total (Prostate Specific Antigen)                                                               
-- PTH - INTACT                                                                                        
-- RBC Count (Red Blood Cell)                                                                          
-- RDW                                                                                                 
-- Reticulocyte Count                                                                                  
-- Semen Analysis - Morphology, Abnormal                                                               
-- Semen Analysis - Morphology, Normal                                                                 
-- Semen Analysis - Motility, Active                                                                   
-- Semen Analysis - Motility, Active.                                                                  
-- Semen Analysis - Motility, Non-motile                                                               
-- Semen Analysis - Motility, Sluggish                                                                 
-- Semen Analysis - Motility, Sluggish.                                                                
-- Semen Analysis - Total Sperm Count                                                                  
-- Semen Analysis - Volume                                                                             
-- Semen Analysis -Percentage Motility ( Grade A + B                                                   
-- Semen Analysis Post wash-Non-Motile                                                                 
-- Semen Analysis post wash-Total Sperm Count                                                          
-- serum creatnine                                                                                     
-- SERUM PROGESTERONE                                                                                  
-- SGOT (AST)                                                                                          
-- SGPT (ALT)                                                                                          
-- Sodium                                                                                              
-- test Himanshu                                                                                       
-- Test123                                                                                             
-- Testosterone, Total                                                                                 
-- TLC                                                                                                 
-- Total IgE                                                                                           
-- Total Leukocyte Count (TLC)                                                                         
-- Triglycerides                                                                                       
-- Troponin-I (Quantitative)                                                                           
-- TSH-Thyroid Stimulating Hormone                                                                     
-- UREA                                                                                                
-- Uric Acid                                                                                           
-- Urine Analysis - pH                                                                                 
-- Urine Analysis - Quantity                                                                           
-- Urine Analysis - Specific Gravity                                                                   
-- Urine Creatinine                                                                                    
-- Urine Creatinine.                                                                                   
-- Urine Microalbumin(n)                                                                               
-- Urine Protein                                                                                       
-- Urine Sodium (Spot)                                                                                 
-- Vitamin B12 



-- FieldName (UNIQUE for both)                                                                                     Source 
-- ---------------------------------------------------------------------------------------------------- -------
-- .Bleeding Time  (BT)1                                                                                IP-Only
-- LDH (Fluid)                                                                                          IP-Only
-- Urine Chloride (Spot)                                                                                IP-Only
-- Urine Potassium (Spot)                                                                               IP-Only
-- Acetone Qualitative                                                                                  OP-Only
-- Bleeding Time  (BT)                                                                                  OP-Only
-- Estradiol (E2)                                                                                       OP-Only
-- Ferritin - Covid                                                                                     OP-Only
-- FSH- Follicle Stimulating Hormone*                                                                   OP-Only
-- GLUCOSE CHALLENGE TEST (GCT)                                                                         OP-Only
-- New123                                                                                               OP-Only
-- Semen Analysis - Morphology, Abnormal                                                                OP-Only
-- Semen Analysis - Morphology, Normal                                                                  OP-Only
-- Semen Analysis - Motility, Active                                                                    OP-Only
-- Semen Analysis - Motility, Active.                                                                   OP-Only
-- Semen Analysis - Motility, Non-motile                                                                OP-Only
-- Semen Analysis - Motility, Sluggish                                                                  OP-Only
-- Semen Analysis - Motility, Sluggish.                                                                 OP-Only
-- Semen Analysis - Total Sperm Count                                                                   OP-Only
-- Semen Analysis - Volume                                                                              OP-Only
-- Semen Analysis -Percentage Motility ( Grade A + B                                                    OP-Only
-- Semen Analysis Post wash-Non-Motile                                                                  OP-Only
-- Semen Analysis post wash-Total Sperm Count                                                           OP-Only
-- SERUM PROGESTERONE                                                                                   OP-Only
-- Test123                                                                                              OP-Only

t1.ValueText, t6.unitname




select top 10 'IPD', t3.RegistrationNo,t1.ValueText, t6.unitname
from diaginvresultip t1
inner join diagsampleiplabmain t2 on t2.diagsampleid = t1.diagsampleid and t2.active = 1
inner join registration t3 on t3.id = t2.registrationid
inner join diagfields t4 on t4.fieldid = t1.fieldid and t4.FieldType = 'N'
inner join itemofservice t5 on t5.serviceid = t2.serviceid
inner join DiagUnitMaster t6 on t6.unitid = t1.unitid
inner join FacilityMaster t7 on t7.FacilityId = t2.FacilityId
where t1.active = 1 and t4.FieldName = 'Haemoglobin Estimation (Hb)' and t3.RegistrationNo = 200670029
order by dateadd(mi, t7.Timezoneoffsetminutes, t2.EncodedDate) desc;