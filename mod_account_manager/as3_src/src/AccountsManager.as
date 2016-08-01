package
{
    import components.*;
    import flash.text.*;
    import net.wg.gui.components.controls.*;
    import net.wg.infrastructure.base.*;
    import scaleform.clik.events.*;
    import flash.events.*;
    import flash.display.*;
    import flash.utils.*;
    import net.wg.gui.login.impl.views.*;

    public class AccountsManager extends AbstractWindowView
    {
        public var py_log: Function;
        public var callFromFlash: Function;
        public var py_getTranslate: Function;
        public var py_setLoginDataById: Function;
        public var py_openAddAccountWindow: Function;

        private var langData: /*LangObject*/ Object;

        private var accountsList: TextField;
        private var newAccButton: SoundButton;
        private var autoEnterCheckBox: CheckBox;
        private var _form: SimpleForm;

        public function AccountsManager()
        {
            super();
            isCentered = true;
        }

        public function as_callToFlash(data_arr:Array):void
        {
            try
            {
                var htmlText: String = "";

                for each (var data:Object in data_arr)
                {
                    htmlText += "<font size='17' color='#FFFFFF'>" + data.user + "<br />" +
                    "<img src='img://gui/maps/icons/library/BattleResultIcon-1.png'> " + data.cluster + "</font><br />" +
                    "<a href='event:0_" + data.id + "'>" + langData.submit_l10n + "</a>    " +
                    "<a href='event:1_" + data.id + "'>" + langData.edit_l10n + "</a>    " +
                    "<a href='event:2_" + data.id + "'>" + langData.delete_l10n + "</a><br />" +
                    "<img width='" + accountsList.width.toString() + "' src='img://gui/flash/AccountsManager/splitter.png'><br /><br />";
                }
                accountsList.htmlText = htmlText;
            }
            catch(err: Error)
            {
                py_log("as_callToFlash " + err.message);
            }
        }

        public function handleLinkClick(e:TextEvent):void
        {
            var action: String = e.text.charAt(0);
            var id: String = e.text.substring(2);

            switch (e.text.charAt(0))
            {
                case "0":
                    action = AM_MODES.SUBMIT;
                    break;
                case "1":
                    action = AM_MODES.EDIT;
                    break;
                case "2":
                    action = AM_MODES.DELETE;
                    break;
            }

            if (action == "submit") {
                py_setLoginDataById(id, _form);
                if (autoEnterCheckBox.selected) {
                    _form.submit.dispatchEvent(new ButtonEvent(ButtonEvent.CLICK));
                }
            } else {
                callFromFlash({
                    "action": action,
                    "id": id
                });
            }
        }

        public function handleAddButtonClick(e:ButtonEvent):void
        {
            py_openAddAccountWindow();
        }

        override protected function onPopulate():void
        {
            super.onPopulate();

            _form = recursiveFindDOC(DisplayObjectContainer(stage), "LoginFormUI") as SimpleForm;

            langData = py_getTranslate();

            window.title = langData.window_title_l10n;
            width = 340;
            height = 530;

            try
            {
                accountsList = new TextField();
                accountsList.x = 10;
                accountsList.y = 10;
                accountsList.width = 320;
                accountsList.height = 490;
                accountsList.multiline = true;
                accountsList.selectable = false;
                //accountsList.background = true;
                //accountsList.border = true;
                accountsList.htmlText = "";
                addChild(accountsList);
                accountsList.addEventListener(TextEvent.LINK, handleLinkClick);

                newAccButton = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
                    label: langData.add_l10n,
                    width: 100,
                    x: 122,
                    y: 500
                })) as SoundButton;

                autoEnterCheckBox = addChild(App.utils.classFactory.getComponent("CheckBox", CheckBox, {
                    label: langData.auto_enter_l10n,
                    x: 10,
                    y: 500,
                    selected: true
                })) as CheckBox;

                newAccButton.addEventListener(ButtonEvent.CLICK, handleAddButtonClick);
            }
            catch (err: Error)
            {
                py_log("onPopulate " + err.message);
            }
        }

        private function recursiveFindDOC(dOC:DisplayObjectContainer, className:String):DisplayObjectContainer
        {
            var child: DisplayObject = null;
            var childOC: DisplayObjectContainer = null;
            var i: int = 0;
            var result: DisplayObjectContainer = null;
            while (i < dOC.numChildren) {
                child = dOC.getChildAt(i);
                if ((child is DisplayObject) && (getQualifiedClassName(child) == className)) result = child as DisplayObjectContainer;
                if (result != null) return result;
                childOC = child as DisplayObjectContainer;
                if ((childOC) && (childOC.numChildren > 0)) result = recursiveFindDOC(childOC, className);
                i++;
            }
            return result;
        }
    }
}
