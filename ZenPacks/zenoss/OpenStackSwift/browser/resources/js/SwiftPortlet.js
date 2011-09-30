var OpenStackSwiftPortlet = YAHOO.zenoss.Subclass.create(
    YAHOO.zenoss.portlet.Portlet);

OpenStackSwiftPortlet.prototype = {
    __class__:"YAHOO.zenoss.portlet.OpenStackSwiftPortlet",

    __init__: function(args) {
        args = args || {};
        id = 'id' in args? args.id : getUID('OpenStackSwiftPortlet');
        title = 'title' in args? args.title: "Swift Cluster";
        bodyHeight = 'bodyHeight' in args? args.bodyHeight: 200;
        refreshTime = 'refreshTime' in args? args.refreshTime: 60;

        datasource = 'datasource' in args? args.datasource :
            new YAHOO.zenoss.portlet.TableDatasource({
                method: 'GET',
                url: '/zport/getSwiftStuff',
                queryArguments: {'system':'/OpenStack/Swift'} 
            });

        this.superclass.__init__({
            id: id, 
            title: title,
            datasource: datasource,
            refreshTime: refreshTime,
            bodyHeight: bodyHeight
        });

        this.buildSettingsPane();
    },

    buildSettingsPane: function() {
        // What to do..
    },

    submitSettings: function(e, settings) {
        this.superclass.submitSettings(e, settings);
    }
};

YAHOO.zenoss.portlet.OpenStackSwiftPortlet = OpenStackSwiftPortlet;
