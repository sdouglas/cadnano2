var msiOpenDatabaseModeTransact = 1;
var msiViewModifyInsert         = 1;
var msiViewModifyUpdate         = 2;
var msiViewModifyAssign         = 3;
var msiViewModifyReplace        = 4;
var msiViewModifyDelete         = 6;

if (WScript.Arguments.Length != 1)
{
	//WScript.StdErr.WriteLine("Usage: " + WScript.ScriptName + " <Product.msi>");
	WScript.echo("Usage: " + WScript.ScriptName + " <Product.msi>");
	WScript.Quit(2);
}

var filespec = WScript.Arguments(0);
var installer
var database

try
{
	installer = WScript.CreateObject("WindowsInstaller.Installer");
	database = installer.OpenDatabase(filespec, msiOpenDatabaseModeTransact);
}
catch(exception)
{
	WScript.echo("Error: Can't find file " + WScript.Arguments(0));
	WScript.Quit(6);
}

var sql;
var view;
var record;

if( database == null )
{
	WScript.echo("Null");
	WScript.Quit(5);
}

// Get the Signature out of the AppSearch table
// WHERE `Property`='REGISTRYVALUE1_X64'
sql = "SELECT * FROM `AppSearch`";
view = database.OpenView(sql);

view.Execute();

while (record = view.Fetch())
{
	var propertyName = record.StringData(1);
	
	var t = propertyName.search("_X64");
	if( t > 0 )
	{
		var signature = record.StringData(2);

		// Find the corresponding value in the RegLocator table
		sql = "SELECT * FROM `RegLocator` WHERE `Signature_`='" + signature + "'";
		var view2 = database.OpenView(sql);
		view2.Execute();
		record = view2.Fetch();

		if (record == null)
		{
			WScript.echo("Unable to find " +propertyName+ " entry in RegLocator table");
		}
		else
		{
			// Add the msidbLocatorType64bit
			if (record.IntegerData(5) < 16)
			{
				record.IntegerData(5) = record.IntegerData(5) + 16;
				view2.Modify(msiViewModifyReplace, record);
			}		
		}
		

		//WScript.echo(record.IntegerData(5));


		view2.Close();
	}
}

view.Close();
database.Commit();