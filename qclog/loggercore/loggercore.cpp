#include "loggercore.h"

#include <qtenvironmentvariables.h>

#include <QFile>
#include <QtSql/QSqlQuery>

LoggerCore::LoggerCore(QString name, QObject * parent) :
    QObject{parent},
    _datadir{find_datadir()},
    _name{name} {

        if (!_datadir.exists()) {
            _datadir.mkpath(".");
        }
        QSqlDatabase db{QSqlDatabase::addDatabase("SQLITE")};
        db.setDatabaseName(_datadir.absoluteFilePath(name + "-ng.db"));

        if (db.open()) {
            _db = db;
        } else {
            throw "Database creation failed";
        }

        QFile f{":/schema.sql"};
        if (!f.open(QFile::ReadOnly | QFile::Text)) {
            throw "Unable to open schema file";
        }

        QTextStream ts{&f};
        auto schema = ts.readAll();

        QSqlQuery q{};
        q.exec(schema);
}

QDir LoggerCore::find_datadir() {
    auto xdh = qEnvironmentVariable("XDG_DATA_HOME");
    auto dd = xdh.isEmpty() ?
        QDir::home().absoluteFilePath(".local/share/qclog") :
        QDir(xdh).absoluteFilePath("qclog");
    return QDir(dd);
}

QString LoggerCore::name() const { return _name; }
