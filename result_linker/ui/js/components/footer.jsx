import React from 'react';
import { Row, Col, Popover, Avatar, Layout} from 'antd';

/*
 * Footer for the website.
*/
export class ResultLinkerFooter extends React.Component {
    render(){
        const { Footer } = Layout;
        return (
            <Footer
                style={{ paddingTop: 10, marginTop: 0, color:'#E3E3E3' , backgroundColor: '#171717', position: 'absolute', bottom: 0, height: '5%', width: '100%', textAlign: 'center', position: "fixed" }}>
                <Row style={{ paddingLeft: 0, paddingTop: 0 }}>
                    <Col span={18}>
                        <p style={{ fontSize: "0.6rem" }}>
                            <b><i>Eureka - SDM Browser</i></b><br />
                            Please create new comment in <a style={{ fontWeight: "bolder" }} href='http://lohsr218.driveline.gkn.com/issues/42535' id="devEmail">
                            #42535 - Result linker</a> for assistance and requests regarding
                            the user interface.
                            If you'd like to discuss the structure
                                , please contact <a style={{ fontWeight: "bolder" }}
                                href='mailto:Ulrich.Scheibe@gkn.com' id="uliEmail">
                                Ulrich Scheibe</a>
                            </p>
                    </Col>
                </Row>
            </Footer>
        )
    }
}
