package
{
    import net.wg.infrastructure.base.*;
    import net.wg.gui.components.controls.*;
    import scaleform.clik.events.*;
    import scaleform.clik.data.*;
    import components.*;

    public class AccountsManagerWindow extends AbstractWindowView
    {
        public var py_log: Function;
        public var py_get_clusters: Function;
        public var py_getTranslate: Function;
        public var py_setAddAccount: Function;
        public var py_setEditAccount: Function;

        private var langData: /*LangObject*/ Object;

        private var wmode: String = AM_MODES.ADD;
        private var submitBtn: SoundButton;
        private var cancelBtn: SoundButton;
        private var showPswd: CheckBox;
        private var titleLabel: TextFieldShort;
        private var emailLabel: TextFieldShort;
        private var passwordLabel: TextFieldShort;
        private var clusterLabel: TextFieldShort;
        private var titleVal: TextInput;
        private var loginVal: TextInput;
        private var passwordVal: TextInput;
        private var clusterVal: DropdownMenu;
        private var qweid: String;

        public function AccountsManagerWindow()
        {
            super();
            isModal = true;
            canClose = true;
            isCentered = true;
        }

        private function handleSubmitBtnClick(e:ButtonEvent):void
        {
            if (titleVal.text == "") {
                titleVal.highlight = true;
                return;
            }
            if (!isValidEmail(loginVal.text)) {
                loginVal.highlight = true;
                return;
            }
            if (wmode == AM_MODES.ADD) {
                py_setAddAccount(titleVal.text, loginVal.text, passwordVal.text, clusterVal.selectedIndex);
            } else if (wmode == AM_MODES.EDIT) {
                py_setEditAccount(qweid, titleVal.text, loginVal.text, passwordVal.text, clusterVal.selectedIndex);
            }
        }

        private function handleCancelBtnClick(e:ButtonEvent):void
        {
            onWindowClose();
        }

        private function handleShowPswdClick(e:ButtonEvent):void
        {
            passwordVal.displayAsPassword = !passwordVal.displayAsPassword;
        }

        public function as_setEditAccountData(id:String, title:String, email:String, password:String, cluster:int):void
        {
            qweid = id;
            titleVal.text = title;
            loginVal.text = email;
            passwordVal.text = password;
            clusterVal.selectedIndex = cluster;
            wmode = AM_MODES.EDIT;
        }

        public function as_setAddAccount():void
        {
            wmode = AM_MODES.ADD;
        }

        override protected function onPopulate():void
        {
            super.onPopulate();

            langData = py_getTranslate();

            window.title = langData.window_title_l10n;
            window.setTitleIcon("team");
            width = 340;
            height = 200;

            try
            {
                // Nickname
                titleLabel = addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
                    label: langData.nick_l10n,
                    selectable: false,
                    showToolTip: false,
                    x: 5,
                    y: 10
                })) as TextFieldShort;

                titleVal = addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
                    width: 210,
                    x: 60,
                    y: 5
                })) as TextInput;

                // Email
                emailLabel = addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
                    label: "Email:",
                    selectable: false,
                    showToolTip: false,
                    x: 5,
                    y: 40
                })) as TextFieldShort;

                loginVal = addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
                    width: 210,
                    x: 60,
                    y: 35
                })) as TextInput;

                // Password
                passwordLabel = addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
                    label: langData.password_l10n,
                    selectable: false,
                    showToolTip: false,
                    x: 5,
                    y: 70
                })) as TextFieldShort;

                passwordVal = addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
                    displayAsPassword: true,
                    width: 210,
                    x: 60,
                    y: 65
                })) as TextInput;

                // Show password
                showPswd = addChild(App.utils.classFactory.getComponent("CheckBox", CheckBox, {
                    label: langData.show_password_l10n,
                    visible: true,
                    x: 60,
                    y: 95
                })) as CheckBox;
                showPswd.addEventListener(ButtonEvent.CLICK, handleShowPswdClick);

                // Cluster
                clusterLabel = addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
                    label: langData.server_l10n,
                    selectable: false,
                    showToolTip: false,
                    x: 5,
                    y: 125
                })) as TextFieldShort;

                var dp:Array = py_get_clusters();
                clusterVal = addChild(App.utils.classFactory.getComponent("DropdownMenu", DropdownMenu, {
                    rowCount: 10,
                    width: 210,
                    x: 60,
                    y: 120,
                    menuDirection: "down",
                    itemRenderer: "DropDownListItemRendererSound",
                    dropdown: "DropdownMenu_ScrollingList",
                    dataProvider: new DataProvider(dp),
                    selectedIndex: 0
                })) as DropdownMenu;

                submitBtn = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
                    label: langData.save_l10n,
                    width: 100,
                    x: 120,
                    y: 165
                })) as SoundButton;
                submitBtn.addEventListener(ButtonEvent.CLICK, handleSubmitBtnClick);

                cancelBtn = addChild(App.utils.classFactory.getComponent("ButtonBlack", SoundButton, {
                    label: langData.cancel_l10n,
                    width: 100,
                    x: 230,
                    y: 165
                })) as SoundButton;
                cancelBtn.addEventListener(ButtonEvent.CLICK, handleCancelBtnClick);
            }
            catch (err: Error)
            {
                py_log("onPopulate " + err.getStackTrace());
            }
        }

        private function isValidEmail(email:String):Boolean
        {
            var emailExpression:RegExp = /([a-zA-Z0-9._-]+?)@([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,4})/;
            return emailExpression.test(email);
        }
    }
}
