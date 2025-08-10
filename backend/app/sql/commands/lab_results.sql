select top 10 {PD}, dateadd(mi,t7.Timezoneoffsetminutes,t2.EncodedDate) OrderDate, t3.RegistrationNo, 
t3.FirstName, t3.MiddleName, t3.LastName, t5.ServiceName, t4.FieldName, t1.ValueText, t6.unitname
from diaginvresult{P} t1
inner join diagsample{P}labmain t2 on t2.diagsampleid = t1.diagsampleid and t2.active = 1
inner join registration t3 on t3.id = t2.registrationid
inner join diagfields t4 on t4.fieldid = t1.fieldid and t4.FieldType = 'N' -- default 'N' (convert it inside the py code)
inner join itemofservice t5 on t5.serviceid = t2.serviceid
inner join DiagUnitMaster t6 on t6.unitid = t1.unitid
inner join FacilityMaster t7 on t7.FacilityId = t2.FacilityId
where t1.active = 1 and t3.RegistrationNo = {REGISTRATIONNO} and t4.FieldName = {FIELDNAME}
order by dateadd(mi, t7.Timezoneoffsetminutes, t2.EncodedDate) desc;
