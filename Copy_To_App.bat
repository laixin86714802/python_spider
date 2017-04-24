
@cd /D E:\SvnJianKe\collect\python\apps

rem ===================================================================
@set TargetDir=E:\SvnJianKe\collect\python\apps
xcopy /e /y .\comm %TargetDir%\taobao_active\comm\*
xcopy /e /y .\comm %TargetDir%\tmall_fcy_all\comm\*
xcopy /e /y .\comm %TargetDir%\tmall_fcy_detail\comm\*
xcopy /e /y .\comm %TargetDir%\kangaiduo_combo\comm\*
xcopy /e /y .\comm %TargetDir%\price_monitor_o3\comm\*
xcopy /e /y .\comm %TargetDir%\email_server\comm\*
xcopy /e /y .\comm %TargetDir%\tmall_health_products\comm\*


rem cpy configure files.
xcopy /e /y .\conf %TargetDir%\taobao_active\conf\*
xcopy /e /y .\conf %TargetDir%\tmall_fcy_all\conf\*
xcopy /e /y .\conf %TargetDir%\tmall_fcy_detail\conf\*
xcopy /e /y .\conf %TargetDir%\kangaiduo_combo\conf\*
xcopy /e /y .\conf %TargetDir%\price_monitor_o3\conf\*
xcopy /e /y .\conf %TargetDir%\email_server\conf\*
xcopy /e /y .\conf %TargetDir%\tmall_health_products\conf\*


pause

