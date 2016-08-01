package
{
    import net.wg.infrastructure.base.*;
    import flash.events.*;
    import flash.display.*;
    import flash.utils.*;
    import components.*;
    import net.wg.gui.login.impl.views.*;
    import net.wg.gui.login.impl.*;

    public class AccountsManagerLoginButton extends AbstractView
    {
        public var py_log: Function;
        public var py_openAccMngr: Function;
        public var py_getTranslate: Function;

        private var isLobby: Boolean = false;
        private var amBtn: AMButton;

        private var _login: LoginPage;
        private var _form: SimpleForm;

        public function AccountsManagerLoginButton()
        {
            super();
        }

        public function as_populateLogin(): void {
            try
            {
                isLobby = false;
                _login = recursiveFindDOC(DisplayObjectContainer(stage), "LoginPageUI") as LoginPage;
                _form = recursiveFindDOC(DisplayObjectContainer(stage), "LoginFormUI") as SimpleForm;

                if (_login != null) {
                    amBtn = new AMButton();
                    amBtn.tooltip = py_getTranslate().tooltip_l10n;
                    _login.addChild(amBtn);
                    addEventListener(Event.RESIZE, resize);
                    amBtn.addEventListener(TextEvent.LINK, handleAMButtonClick);
                    resize();
                }
            }
            catch (err: Error)
            {
                py_log("as_populateLogin " + err.getStackTrace());
            }
        }

        public function as_populateLobby():void
        {
            isLobby = true;
        }

        private function resize(e:Event = null):void
        {
            if (!isLobby) {
                try
                {
                    amBtn.x = _form.parent.x + _form.keyboardLang.x;
                    amBtn.y = _form.parent.y + _form.submit.y;
                }
                catch (err: Error)
                {
                    py_log("resize " + err.getStackTrace());
                }
            }
        }

        private function handleAMButtonClick(e:TextEvent):void
        {
            py_openAccMngr();
        }

        private function recursiveFindDOC(dOC:DisplayObjectContainer, className:String):DisplayObjectContainer
        {
            var child: DisplayObject = null;
            var childOC: DisplayObjectContainer = null;
            var i: int = 0;
            var result:DisplayObjectContainer = null;
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
