# Замена логики "Приложение-> Модели" на "Секции->Модели
# надеюсь решение временное
# {'название секции': [app.Model1, app.Model2, ... app.ModelN]}
ADMIN_SECTIONS = {

    'СИСТЕМНЫЕ':        [{"model": 'remotes.RemoteService', "hidden": False}, {"model": 'notifications.NotifyItem', "hidden": False}, {"model": 'permission.Page', "hidden": False}, {"model": 'xlsexport.ExportTemplate', "hidden": False}, {"model": 'xlsexport.ImportTemplate', "hidden": False}],

    'ЖУРНАЛЫ':          [{"model": 'applogs.ClientRecord', "hidden": False}, {"model": 'applogs.ServerRecord', "hidden": False}, {"model": 'easy_log.LogItem', "hidden": False}, {"model": 'easy_log.LogJournal', "hidden": False}, {"model": 'axes.AccessAttempt', "hidden": False}, {"model": 'axes.AccessLog', "hidden": False}],

    'ДОСТУП':           [{"model": 'permission.AccessRole', "hidden": False}, {"model": 'permission.AccessProfile', "hidden": False}, {"model": 'auth.User', "hidden": False}, {"model": 'auth.Group', "hidden": False}, {"model": 'authtoken.Token', "hidden": False}],

    'КОМПАНИИ':         [{"model": 'outsource.Headquater', "hidden": False}, {"model": 'outsource.Organization', "hidden": False}, {"model": 'outsource.Agency', "hidden": False}, {"model": 'outsource.OrgLink', "hidden": False}],

    'СОТРУДНИКИ':       [{"model": 'outsource.Job', "hidden": False}, {"model": 'employees.DocType', "hidden": False}, {"model": 'employees.AgencyEmployee', "hidden": False}, {"model": 'employees.AgencyManager', "hidden": False}, {"model": 'employees.EmployeeEvent', "hidden": False}, {"model": 'employees.EmployeeHistory', "hidden": False},
                         {"model": 'employees.JobHistory', "hidden": True}, {"model": 'employees.OrgHistory', "hidden": True}, {"model": 'employees.EmployeeDoc', "hidden": True}, {"model": 'violations.ViolationRule', "hidden": False}],

    'ЗАПРОСЫ НА ПЕРСОНАЛ':  [{"model": 'shifts.OutsourcingRequest', "hidden": False}],

    'ПРОМОУТЕРЫ':       [{"model": 'outsource.StoreArea', "hidden": False}, {"model": 'outsource.QuotaVolume', "hidden": False}, {"model": 'outsource.Quota', "hidden": False}, {"model": 'shifts.PromoShift', "hidden": False}, {"model": 'outsource.QuotaInfo', "hidden": False}, {"model": 'shifts.Availability', "hidden": False}],

    'ПРЕТЕНЗИИ':        [{"model": 'claims.ClaimRequest', "hidden": False}, {"model": 'claims.ClaimType', "hidden": False}, {"model": 'claims.ClaimStatus', "hidden": False}, {"model": 'claims.ClaimAction', "hidden": False}],
}
ADMIN_COLUMNS = [
    ('СИСТЕМНЫЕ', 'ЖУРНАЛЫ', 'ДОСТУП'),
    ('КОМПАНИИ', 'СОТРУДНИКИ', 'ЗАПРОСЫ НА ПЕРСОНАЛ', 'ПРОМОУТЕРЫ', 'ПРЕТЕНЗИИ'),
]