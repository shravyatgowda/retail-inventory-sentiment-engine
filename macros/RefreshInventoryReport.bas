Attribute VB_Name = "RefreshInventoryReport"
' =========================================================
' RefreshInventoryReport
' Dynamically ingests the clean_inventory.csv produced by
' src/pipeline.py and rebuilds the weekly reporting sheet.
'
' Install: Excel > Developer > Visual Basic > Import File
' Run: Developer > Macros > RefreshInventoryReport
' =========================================================

Sub RefreshInventoryReport()

    Dim wsData As Worksheet
    Dim wsReport As Worksheet
    Dim csvPath As String
    Dim lastRow As Long, lastCol As Long

    csvPath = ThisWorkbook.Path & "\clean_inventory.csv"

    If Dir(csvPath) = "" Then
        MsgBox "clean_inventory.csv not found next to this workbook." & vbCrLf & _
               "Run: python src/pipeline.py --out clean_inventory.csv", vbExclamation
        Exit Sub
    End If

    ' --- Refresh raw data sheet from CSV ---
    On Error Resume Next
    Set wsData = ThisWorkbook.Sheets("RawData")
    On Error GoTo 0
    If wsData Is Nothing Then
        Set wsData = ThisWorkbook.Sheets.Add
        wsData.Name = "RawData"
    Else
        wsData.Cells.Clear
    End If

    With wsData.QueryTables.Add(Connection:="TEXT;" & csvPath, Destination:=wsData.Range("A1"))
        .TextFileParseType = xlDelimited
        .TextFileCommaDelimiter = True
        .TextFileConsecutiveDelimiter = False
        .Refresh BackgroundQuery:=False
    End With

    lastRow = wsData.Cells(wsData.Rows.Count, 1).End(xlUp).Row
    lastCol = wsData.Cells(1, wsData.Columns.Count).End(xlToLeft).Column

    ' --- Build/refresh pivot-style summary on Report sheet ---
    On Error Resume Next
    Set wsReport = ThisWorkbook.Sheets("Report")
    On Error GoTo 0
    If wsReport Is Nothing Then
        Set wsReport = ThisWorkbook.Sheets.Add
        wsReport.Name = "Report"
    Else
        wsReport.Cells.Clear
    End If

    wsReport.Range("A1").Value = "Inventory Report — Generated " & Format(Now, "yyyy-mm-dd hh:mm")
    wsReport.Range("A3").Value = "Total SKUs"
    wsReport.Range("B3").Value = "=COUNTA(RawData!A2:A" & lastRow & ")"
    wsReport.Range("A4").Value = "SKUs Below Reorder Point"
    wsReport.Range("B4").Value = "=COUNTIF(RawData!E2:E" & lastRow & ",TRUE)"
    wsReport.Range("A5").Value = "Total Inventory Value"
    wsReport.Range("B5").Value = "=SUM(RawData!F2:F" & lastRow & ")"

    wsReport.Columns("A:B").AutoFit
    wsReport.Activate

    MsgBox "Inventory report refreshed from " & lastRow - 1 & " rows.", vbInformation

End Sub
